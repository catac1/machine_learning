from fastapi import APIRouter, Body
import numpy as np
import joblib

router = APIRouter(prefix="/api/fish", tags=["fish"])

model = joblib.load("./pkl/20260519_lasso.joblib")

def _model_name(pipeline):
    steps = " + ".join(
        type(step).__name__ + (
            f"(degree={step.degree})" if hasattr(step, "degree") else
            f"(alpha={step.alpha})"   if hasattr(step, "alpha")  else ""
        )
        for _, step in pipeline.steps
    )
    return steps

FISH_CSV_URL = "http://114.207.245.181:13000/csv/fish01.csv"


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


# 127.0.0.1:8000/api/fish/scatter
# Returns actual vs predicted weight for all Perch samples
@router.get("/scatter")
async def scatter_data():
    try:
        import pandas as pd
        from sklearn.metrics import r2_score, root_mean_squared_error

        df = pd.read_csv(FISH_CSV_URL)
        perch = df[df["Species"] == "Perch"][["Length", "Width", "Height", "Weight"]]

        X = perch[["Length", "Width", "Height"]].values
        y_actual = perch["Weight"].values
        y_pred = model.predict(X)

        return {
            "actual": y_actual.tolist(),
            "predicted": y_pred.tolist(),
            "r2": round(r2_score(y_actual, y_pred), 4),
            "rmse": round(root_mean_squared_error(y_actual, y_pred), 2),
            "model_name": _model_name(model),
            "feature_range": {
                "length": {"min": float(perch["Length"].min()), "max": float(perch["Length"].max())},
                "width":  {"min": float(perch["Width"].min()),  "max": float(perch["Width"].max())},
                "height": {"min": float(perch["Height"].min()), "max": float(perch["Height"].max())},
            },
        }
    except Exception as e:
        return {"message": str(e)}
