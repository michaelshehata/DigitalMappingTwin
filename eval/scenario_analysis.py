import numpy as np
import matplotlib.pyplot as plt
import joblib
import json
import sys
import os

sys.path.insert(0, "..")

from scripts.load_data import load_all_data

models_to_eval = ["random_forest", "xgboost", "lightgbm"]

X, y, _ = load_all_data()

os.makedirs("outputs/eval", exist_ok=True)

print("="*70)
print("SCENARIO ANALYSIS")
print("="*70)

scenario_results = {}

fig = plt.figure(figsize=(16, 10))

for model_idx, model_name in enumerate(models_to_eval):
    try:
        model = joblib.load(f"model_output/{model_name}.pkl")

        with open(f"model_output/{model_name}_metrics.json", "r") as f:
            metrics = json.load(f)
        optimal_threshold = metrics.get("optimal_threshold", 0.3)

        print(f"\n{model_name.upper()} Scenarios (threshold={optimal_threshold:.2f}):")

        def run_scenario(X_mod):
            X_flat = X_mod.reshape(-1, X_mod.shape[-1])
            preds = []
            chunk_size = 100000

            for i in range(0, len(X_flat), chunk_size):
                chunk = X_flat[i:i + chunk_size]
                prob = model.predict_proba(chunk)[:, 1]
                pred = (prob > optimal_threshold).astype(int)
                preds.append(pred)

            preds = np.concatenate(preds)
            return preds.reshape(y.shape)

        # Baseline
        baseline = run_scenario(X)
        baseline_change_pct = 100 * np.sum(baseline) / baseline.size

        # Urban Growth Scenario: +50% population
        X_growth = X.copy()
        X_growth[..., 1] = np.minimum(X_growth[..., 1] * 1.5, 1.0)
        growth = run_scenario(X_growth)
        growth_change_pct = 100 * np.sum(growth) / growth.size

        # Conservation Scenario: +20% vegetation
        X_conserve = X.copy()
        X_conserve[..., 0] = np.minimum(X_conserve[..., 0] * 1.2, 1.0)
        conserve = run_scenario(X_conserve)
        conserve_change_pct = 100 * np.sum(conserve) / conserve.size

        # Climate Stress Scenario: +2 deg C temperature
        X_climate = X.copy()
        X_climate[..., 2] = np.minimum(X_climate[..., 2] + 0.1, 1.0)
        climate = run_scenario(X_climate)
        climate_change_pct = 100 * np.sum(climate) / climate.size

        scenario_results[model_name] = {
            "baseline": float(baseline_change_pct),
            "urban_growth": float(growth_change_pct),
            "conservation": float(conserve_change_pct),
            "climate_stress": float(climate_change_pct),
            "threshold": float(optimal_threshold)
        }

        print(f"  Baseline:          {baseline_change_pct:.2f}% change")
        print(f"  Urban Growth:      {growth_change_pct:.2f}% change ({growth_change_pct - baseline_change_pct:+.2f}%)")
        print(f"  Conservation:      {conserve_change_pct:.2f}% change ({conserve_change_pct - baseline_change_pct:+.2f}%)")
        print(f"  Climate Stress:    {climate_change_pct:.2f}% change ({climate_change_pct - baseline_change_pct:+.2f}%)")

        # Plot scenarios for this model
        row = model_idx
        axes = []

        for col, (title, pred_map) in enumerate([
            ("Baseline", baseline),
            ("Urban Growth\n(+50% Pop)", growth),
            ("Conservation\n(+20% NDVI)", conserve),
            ("Climate Stress\n(+2°C)", climate)
        ]):
            ax = fig.add_subplot(3, 4, row * 4 + col + 1)
            im = ax.imshow(pred_map, cmap="RdYlBu_r", vmin=0, vmax=1)
            ax.set_title(f"{model_name.upper()}\n{title}", fontsize=10, fontweight='bold')
            ax.axis('off')
            plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    except FileNotFoundError:
        print(f"\n{model_name.upper()}: Model file not found (placeholder)")
        scenario_results[model_name] = {
            "baseline": 0.0,
            "urban_growth": 0.0,
            "conservation": 0.0,
            "climate_stress": 0.0,
            "threshold": 0.3
        }
        for col in range(4):
            ax = fig.add_subplot(3, 4, model_idx * 4 + col + 1)
            ax.text(0.5, 0.5, f"{model_name}\n(Not trained)",
                   ha='center', va='center', transform=ax.transAxes)
            ax.axis('off')

plt.suptitle("Scenario Analysis: Land Cover Change Predictions", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig("outputs/eval/scenario_analysis.png", dpi=150, bbox_inches='tight')
print("\n\nScenario analysis saved to: outputs/eval/scenario_analysis.png")

with open("outputs/eval/scenario_results.json", "w") as f:
    json.dump(scenario_results, f, indent=2)
print("Results saved to: outputs/eval/scenario_results.json")
