# app / routers / member.py

from fastapi import APIRouter, Body
from app.database import customer
from app.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/customer")


@router.post("/join.do")
async def member_join(
    email: str = Body(...),
    name: str = Body(...),
    password: str = Body(...),
    phone: str = Body(...),
):
    try:
        hashed_password = hash_password(password)
        ret = await customer.insert_one(
            {
                "email": email,
                "name": name,
                "password": hashed_password,
                "phone": phone,
            }
        )
        if ret.acknowledged:
            return {"result": {"affectedRows": 1}}
        return {"result": {"affectedRows": 0}}
    except Exception as e:
        return {"message": str(e)}


@router.post("/login.do")
async def member_login(email: str = Body(...), password: str = Body(...)):
    try:
        ret = await customer.find_one({"email": email}, {"_id": 0})
        if ret and verify_password(password, ret["password"]):
            access_token = create_access_token(email)
            refresh_token = create_refresh_token(email)
            return {
                "result": 1,
                "accessToken": access_token,
                "refreshToken": refresh_token,
            }
        return {"result": 0, "message": "로그인 실패"}
    except Exception as e:
        return {"message": str(e)}
