import os
import json
import pandas as pd


# BASE DIRECTORY
BASE_DIR = "model_output/hyperparameter_tuning"

OUTPUT_CSV = "model_output/hyperparameter_tuning/experiment_results.csv"


# FIND ALL METRICS FILES RECURSIVELY
metric_files = []

for root, dirs, files in os.walk(BASE_DIR):

    for file in files:

        if file.endswith("_metrics.json"):

            metric_files.append(
                os.path.join(root, file)
            )


# LOAD RESULTS
results = []

for metric_path in metric_files:

    try:

        with open(metric_path, "r") as f:

            metrics = json.load(f)

        row = {

            "Experiment": metrics.get("experiment_name"),

            "Model": metrics.get("model"),

            "F1": metrics.get("test_f1"),

            "Precision": metrics.get("test_precision"),

            "Recall": metrics.get("test_recall"),

            "PR-AUC": metrics.get("test_pr_auc"),

            "AUROC": metrics.get("test_auroc"),

            "Specificity": metrics.get("test_specificity"),

            "Threshold": metrics.get("optimal_threshold"),

            "TP": metrics.get("true_positives"),

            "FP": metrics.get("false_positives"),

            "TN": metrics.get("true_negatives"),

            "FN": metrics.get("false_negatives"),

            "n_estimators": metrics.get("n_estimators"),

            "max_depth": metrics.get("max_depth"),

            "learning_rate": metrics.get("learning_rate"),

            "num_leaves": metrics.get("num_leaves"),

            "scale_pos_weight": metrics.get("scale_pos_weight"),

            "class_weight": metrics.get("class_weight")
        }

        results.append(row)

    except Exception as e:

        print(f"\nError reading: {metric_path}")
        print(str(e))


# CREATE DATAFRAME
df = pd.DataFrame(results)


# SORT BY F1
df = df.sort_values(
    by="F1",
    ascending=False
)


# SAVE CSV
df.to_csv(
    OUTPUT_CSV,
    index=False
)


print("HYPERPARAMETER TUNING RESULTS")


print(
    df.to_string(index=False)
)


# BEST MODELS
print("BEST MODELS")

for metric in ["F1", "Precision", "Recall", "PR-AUC", "AUROC"]:

    best_row = df.sort_values(
        metric,
        ascending=False
    ).iloc[0]

    print(
        f"\nBest {metric}: "
        f"{best_row['Experiment']} "
        f"({best_row[metric]:.4f})"
    )


# OVERALL BEST MODEL
best_model = df.iloc[0]


print("OVERALL BEST MODEL")


print(f"\nExperiment: {best_model['Experiment']}")
print(f"Model Type: {best_model['Model']}")
print(f"F1 Score:   {best_model['F1']:.4f}")
print(f"Precision:  {best_model['Precision']:.4f}")
print(f"Recall:     {best_model['Recall']:.4f}")
print(f"PR-AUC:     {best_model['PR-AUC']:.4f}")
print(f"AUROC:      {best_model['AUROC']:.4f}")



print(f"\nSaved to:")
print(OUTPUT_CSV)