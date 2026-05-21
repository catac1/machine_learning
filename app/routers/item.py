# app/routers/item.py

from fastapi import APIRouter, Form, File, UploadFile, Body
from app.database import item, get_next_sequence
from datetime import datetime

from fastapi.responses import StreamingResponse, FileResponse
from io import BytesIO
from pathlib import Path
import uuid
import os

BASE_DIR = Path(__file__).resolve().parent.parent
filePath = BASE_DIR / "uploads"
print(filePath)

router = APIRouter(prefix="/api/item", tags=["item"])


# 이미지표시 => 127.0.0.0.1:8000/api/item/image1?no=1
# GET방식
@router.get("/image1")
async def get_image1(no: int):
    try:
        query = {"no": no}
        projection = {"filename": 1, "filetype": 1}
        t1 = await item.find_one(query, projection)
        if t1:
            return FileResponse(path=t1["filename"], media_type=t1["filetype"])
        else:
            return {"message": "이미지를 찾을 수 없습니다."}
    except Exception as e:
        return {"message": str(e)}


# 이미지 등록 => 127.0.0.0.1:8000/api/item/insert1
# POST방식으로 title, description, price, file
@router.post("/insert1")
async def insert_item1(
    title: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    file: UploadFile = File(...),
):
    try:
        # 확장자
        # old method
        # ext = os.path.splitext(file.filename)[1]
        # new method for python 3.4
        ext = Path(file.filename).suffix
        filename = f"{uuid.uuid4()}{ext}"

        # 파일저장 위치
        # new method: OS agnostic. requires str() to serialize
        save_path = filePath / filename
        # old method: this isn't OS agnostic
        # save_path = f"{filePath}/{filename}"

        # 바이트스트림으로 읽어서 저장
        with open(save_path, "wb") as f:
            f.write(await file.read())

        t1 = {
            "no": await get_next_sequence("item"),
            "title": title,
            "description": description,
            "filename": str(save_path),
            "filetype": file.content_type,
            "filesize": file.size,
            "create_at": datetime.now(),
        }
        ret = await item.insert_one(t1)
        return {"message": "success", "insert_id": str(ret.inserted_id)}
    except Exception as e:
        return {"message": str(e)}


# 이미지표시 => 127.0.0.0.1:8000/api/item/image?no=1
# GET방식
@router.get("/image")
async def get_image(no: int):
    try:
        query = {"no": no}
        # 0 빼기 1 가져오기. 혼용 X
        # projection = {"_id": 0}
        projection = {"filedata": 1, "filetype": 1}
        t1 = await item.find_one(query, projection)
        if t1:
            return StreamingResponse(BytesIO(t1["filedata"]), media_type=t1["filetype"])
        else:
            return {"message": "이미지를 찾을 수 없습니다."}
    except Exception as e:
        return {"message": str(e)}


# 이미지 등록 => 127.0.0.0.1:8000/api/item/insert
# POST방식으로 title, description, price, file
@router.post("/insert")
async def insert_item(
    title: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    file: UploadFile = File(...),
):
    try:
        t1 = {
            "no": await get_next_sequence("item"),
            "title": title,
            "description": description,
            "filename": file.filename,
            "filedata": await file.read(),
            "filetype": file.content_type,
            "filesize": file.size,
            "create_at": datetime.now(),
        }
        ret = await item.insert_one(t1)
        return {"message": "success", "insert_id": str(ret.inserted_id)}
    except Exception as e:
        return {"message": str(e)}
