from contextlib import asynccontextmanager
from fastapi import APIRouter, Body
import numpy as np
import joblib

model = None


@asynccontextmanager
async def lifespan(app):
    global model
    with joblib.parallel_backend("threading"):
        model = joblib.load("./pkl/20260519_lasso.joblib")
    yield
    model = None


router = APIRouter(prefix="/api/fish", tags=["fish"])


# 127.0.0.1:8000/api/fish/predict
# { "length": 20, "width": 10, "height": 5}
@router.post("/predict")
async def predict_fish(
    length: float = Body(...),
    width: float = Body(...),
    height: float = Body(...),
):
    try:
        sample = np.array([[length, width, height]])
        pred = model.predict(sample)
        return {"predict": pred[0]}
    except Exception as e:
        return {"message": str(e)}
