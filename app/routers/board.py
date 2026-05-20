# app / routers / board.py

from fastapi import APIRouter, Body
from app.database import board, get_next_sequence
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/board")

# 게시글 상세
# 127.0.0.1:8000/api/board/detail?no=1
@router.get("/detail")
async def detail_board(no: int):
    try:
        query= {"no": no}
        projection = {"_id": 0}
        ret = await board.find_one(query, projection)
        if not ret:
            return {"message":"글이 없습니다" }
        return ret
    except Exception as e:
        return {"message": str(e) }

# 게시글 삭제
# 127.0.0.1:8000/api/board/delete
@router.delete("/delete")
async def delete_board(
    id: str = Body(embed=True)):
    try:
        query = {"_id": ObjectId(id)}
        ret = await board.delete_one(query)
        print(ret)
        if ret.deleted_count == 1:
            return {"message":"글이 삭제되었습니다" }
        return {"message":"삭제할 글이 없습니다" }
    except Exception as e:
        return {"message":str(e) }

# 게시글 변경 
# 127.0.0.1:8000/api/board/update
@router.put("/update")
async def update_board(
    title: str = Body(...),
    content: str = Body(...),
    author: str = Body(...),
    # id: str = Body(...)
    no: int = Body(...)
    ):
    try:
        query = {"no": no}
        # query = {"_id": ObjectId(id)}
        update = {"$set": {"title": title, "content": content, "author": author}}
        ret = await board.update_one(query, update)
        print(ret)
        if ret.modified_count == 1: 
            return {"message": "글이 수정되었습니다."}
        return {"message": "수정할 글이 없습니다.."}
    except Exception as e:
        return {"message": str(e)}

# 전체 글 보기
# 127.0.0.1:8000/api/board/listpage?page=1&limit=10
@router.get("/listpage")
async def list_page(page:int = 1, limit:int = 10):
    try:
        query = {}
        projection = {"_id": 0}
        skip = (page - 1)*limit
        sort = {'_id': -1}
        total = await board.count_documents(query)
        writings = await board.find(query, projection).sort(sort).skip(skip) \
            .limit(limit).to_list(length=limit)
        return { 'total': total, 'writings': writings }
    except Exception as e:
        return {"message": str(e)}

# 전체 글 보기
# 127.0.0.1:8000/api/board/list
@router.get("/list")
async def list_board():
    try:
        query = {}
        projection = {'_id': 0}
        return await board.find(query, projection).to_list(length=100)
    except Exception as e:
        return {"message": str(e)}

# 글쓰기
# 127.0.0.1:8000/api/board/write
@router.post("/write")
async def write_board(
    title:str = Body(...),
    content:str = Body(...),
    author:str = Body(...)):
    try:
        seq = await get_next_sequence("board")
        await board.insert_one({
            "no": seq,
            "title":title,
            "content":content,
            "author":author,
            "create_at": datetime.now(),
        })
        return {"message": "글이 작성되었습니다."}
    except Exception as e:
        return {"message": str(e)}