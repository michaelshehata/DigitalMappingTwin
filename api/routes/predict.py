from fastapi import APIRouter

from api.services.inference import run_prediction

router = APIRouter()

@router.post("/predict")
def predict(
    threshold: float = 0.35,
    steps: int = 10
):

    result = run_prediction(
        threshold=threshold,
        steps=steps
    )

    return result