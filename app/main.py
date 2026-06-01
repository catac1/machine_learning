# 파일명 : app / main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routers import board, member, item, fish, predict
import joblib
from tensorflow.keras.models import load_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load("./pkl/20260519_lasso.joblib")
    app.state.image_model = joblib.load("./pkl/20260527_image_model.joblib")
    app.state.deep_model = load_model("./pkl/20260601_handwritten.keras")
    app.state.cnn_flower_model = load_model(
        "./pkl/20260601_flower_efficientnetv2.keras"
    )
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(board.router)
app.include_router(member.router)
app.include_router(item.router)
app.include_router(fish.router)
app.include_router(predict.router)
