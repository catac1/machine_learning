from fastapi import APIRouter, Body, File, Request, UploadFile, Form
from fastapi.responses import JSONResponse
import numpy as np
from PIL import Image
import io

router = APIRouter(prefix="/api/predict", tags=["predict"])


@router.post("/number")
async def predict_number(request: Request, file: UploadFile = File(...)):
    try:
        # 1. 이미지 받기
        content = await file.read()

        # 2. 흑백이미지로 변환
        image = Image.open(io.BytesIO(content)).convert("L")

        # 3. 이미지 크기를 28*28로 변환
        image = image.resize((28, 28))

        # 4. 이미지를 배열로 변경하기
        image_array = np.array(image)

        # 4-1. inverte amge
        image_array = 255 - image_array

        # 5. (1, 784)로 변경
        # input_input = image_array.reshape(1, 784)
        # print(input_input)
        # 6. 예측
        model = request.app.state.handwritten_model
        # pred = model.predict(input_input)
        pred = model.predict(image_array[None, ...])
        pred_final = np.argmax(pred, axis=1)
        print(pred_final)
        return {"pred": str(pred_final), "status": "ok"}
    except Exception as e:
        print(e)
        return {"message": str(e)}


@router.post("/deep_number")
async def predict_deep_number(request: Request, file: UploadFile = File(...)):
    try:
        # 1. 이미지 받기
        content = await file.read()

        # 2. 흑백이미지로 변환
        image = Image.open(io.BytesIO(content)).convert("L")

        # 3. 이미지 크기를 28*28로 변환
        image = image.resize((28, 28))

        # 4. 이미지를 배열로 변경하기
        image_array = np.array(image)

        # 5. invert amge
        image_array = 255 - image_array

        # 6. 예측
        model = request.app.state.deep_model
        # pred = model.predict(input_input)
        pred = model.predict(image_array[None, ...])
        pred_final = np.argmax(pred, axis=1)
        print(pred_final)
        return {"pred": str(pred_final), "status": "ok"}
    except Exception as e:
        print(e)
        return {"message": str(e)}


@router.post("/cnn_flower")
async def predict_cnn_flower(request: Request, file: UploadFile = File(...)):
    try:
        # 1. 이미지 받기
        content = await file.read()

        # 2. 흑백이미지로 변환
        image = Image.open(io.BytesIO(content))

        # 3. 이미지 크기를 28*28로 변환
        image = image.resize((224, 224))

        # 4. 이미지를 배열로 변경하기
        image_array = np.array(image)

        # # 5. invert amge
        # image_array = 255 - image_array

        # 6. 예측
        model = request.app.state.cnn_flower_model
        # pred = model.predict(input_input)
        pred = model.predict(image_array[None, ...])
        pred_final = np.argmax(pred, axis=1)

        flower_classes = ["daisy", "dandelion", "roses", "sunflowers", "tulips"]
        index = pred_final[0]
        return {"pred": flower_classes[index], "status": "ok"}
    except Exception as e:
        print(e)
        return {"message": str(e)}
