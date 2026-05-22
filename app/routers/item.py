# app/routers/item.py

from fastapi import APIRouter, Form, File, UploadFile, Body
from app.database import item, react_item, get_next_sequence
from datetime import datetime

from fastapi.responses import StreamingResponse, FileResponse
from io import BytesIO
from pathlib import Path
import uuid
import os
from typing import Optional
import struct

from bson import ObjectId, BSON

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
async def insert_image1(
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
async def insert_image(
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


@router.post("/insert.do")
async def item_insert(
    name: str = Body(...),
    detail: str = Body(...),
    price: int = Body(...),
    qty: int = Body(...),
    phone: str = Body(...),
):
    try:
        no = await get_next_sequence("react_item")
        print(f"no => {no}")
        print(f"{name} {detail} {price} {qty} {phone}")
        ret = await react_item.insert_one(
            {
                "no": no,
                "detail": detail,
                "price": price,
                "qty": qty,
                "phone": phone,
                "create_at": datetime.now(),
            }
        )
        if ret.acknowledged:
            return {"message": "success", "result": {"affectedRows": 1}}
        return {"message": "failure", "affectedRows": 0}
    except Exception as e:
        return {"message": "success", "affectedRows": 1}


@router.get("/list.do")
async def item_list(page: int, cnt: int, search: str | None = None):
    try:
        query = {}
        projection = {"_id": 0}
        ret = await react_item.find(query, projection).to_list()
        result = [
            {"code": i, "name": "foo", "phone": "000-111-01010"} | r
            for (i, r) in zip(range(1, len(ret)), ret)
        ]
        return {
            "message": "success",
            "status": 200,
            "total": len(ret),
            "result": result,
        }
    except Exception as e:
        return {"message": str(e)}


# 물품목록 => 127.0.0.1:8000/api/item/list?page=1&limit=10
@router.get("/list")
async def get_item_list(page: int = 1, limit: int = 10):
    try:
        query = {}

        projection = {
            "_id": 1,
            "filetype": 0,
            "filename": 0,
            "filesize": 0,
        }
        skip = (page - 1) * limit

        total = await item.count_documents(query)
        t1 = await item.find(query, projection).skip(skip).limit(limit).to_list(limit)

        # 반복문을 사용해서 새로운 imgurl 생성
        for doc in t1:
            id_bson = doc["_id"]
            print_bson(id_bson)
            doc["_id"] = str(id_bson)
            if doc.pop("filedata", None) is not None:
                doc["imgurl"] = f"/api/item/image?no={doc['no']}"
            else:
                doc["imgurl"] = f"/api/item/image1?no={doc['no']}"

        return {"list": t1, "total": total}
    except Exception as e:
        return {"message": str(e)}


# 물품목록 => 127.0.0.1:8000/api/item/list1?page=1&limit=10
@router.get("/list1")
async def get_item_list(page: int = 1, limit: int = 10):
    try:
        query = {}

        projection = {
            "_id": 0,
            # "filedata": 1,
            "filetype": 0,
            "filename": 0,
            "filesize": 0,
        }
        skip = (page - 1) * limit

        total = await item.count_documents(query)
        t1 = await item.find(query, projection).skip(skip).limit(limit).to_list(limit)

        # 반복문을 사용해서 새로운 imgurl 생성
        for doc in t1:
            if doc.pop("filedata", None) is not None:
                doc["imgurl"] = f"/api/item/image?no={doc['no']}"
            else:
                doc["imgurl"] = f"/api/item/image1?no={doc['no']}"
        return {"list": t1, "total": total}
    except Exception as e:
        return {"message": str(e)}


def print_bson(oid):
    timestamp_raw, random_value, counter = struct.unpack(">I5s3s", oid.binary)
    print(f"--- Information Inside ObjectId: {oid} ---")
    print(f"1. Creation Time (Unix Epoch): {timestamp_raw} seconds")
    print(f"2. Human-Readable Date:       {oid.generation_time}")
    print(f"3. Unique Process/Machine ID:  0x{random_value.hex()}")
    print(f"4. Sequential Counter Value:   {int.from_bytes(counter, byteorder='big')}")
