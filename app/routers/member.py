from fastapi_jwt import JwtAccessBearer, JwtRefreshBearer, JwtAuthorizationCredentials
from fastapi import APIRouter, Body, Form, Depends
from datetime import datetime, timedelta
from app.database import member
from passlib.context import CryptContext

router = APIRouter(prefix="/api/member", tags=["member"])

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# 암호 해쉬 함수
def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)


# 암호 비교 함수
def verify_password(pw1: str, pw2: str) -> bool:
    return pwd_context.verify(pw1, pw2)


# access_token (HMAC + SHA256)
access_token = JwtAccessBearer(
    secret_key="thisislonglonglonglongaccess",
    auto_error=True,
    access_expires_delta=timedelta(minutes=30),
)

# refresh_token (HMAC + SHA256)
refresh_token = JwtRefreshBearer(
    secret_key="thisislonglonglonglongrefresh",
    auto_error=True,
    refresh_expires_delta=timedelta(days=1),
)


# 회원비밀번호 변경 => 127.0.0.1:8000/api/member/updatepw
# {"pw": "a", "newpw": "b"}
@router.put("/updatepw")
async def updatepw(
    credentials: JwtAuthorizationCredentials = Depends(access_token),
    newpw: str = Body(embed=True),
):
    try:
        id = credentials["id"]
        ret = await member.find_one({"id": id})
        if not ret:
            {"result": -1, "message": "존재하지 않는 아이디 입니다."}
        hashed_pw = hash_password(newpw)
        t1 = {"pw": hashed_pw}
        ret = await member.update_one({"id": id}, {"$set": t1})
        return {"result": 1, "acknowledged": str(ret.acknowledged)}
    except Exception as e:
        print(e)
        return {"result": 0, "message": str(e)}


# 회원탈퇴 => 127.0.0.1:8000/api/member/delete
# {"id": "a", "pw": "1234", "name": "aa", "phone": "010-1234-5678"}
# Depends <= 메모리에 로딩되어 있는지 미리 체크
@router.delete("/delete")
async def update(
    credentials: JwtAuthorizationCredentials = Depends(access_token),
    pw: str = Body(embed=True),
):
    try:
        id = credentials.subject["id"]
        ret = await member.find_one({"id": id})
        if not ret:
            {"result": -1, "message": "존재하지 않는 아이디 입니다."}

        if not verify_password(pw, ret["pw"]):
            {"result": -2, "message": "비밀번호가 일치하지 않습니다."}

        ret = await member.delete_one({"id": id})
        return {"result": 1, "deleted_count": str(ret.deleted_count)}
    except Exception as e:
        print(e)
        return {"result": 0, "message": str(e)}


# 정보변경 => 127.0.0.1:8000/api/member/update
# {"id": "a", "pw": "1234", "name": "aa", "phone": "010-1234-5678"}
# Depends <= 메모리에 로딩되어 있는지 미리 체크
@router.put("/update")
async def update(
    credentials: JwtAuthorizationCredentials = Depends(access_token),
    name: str = Body(...),
    phone: str = Body(...),
):
    try:
        id = credentials.subject["id"]
        t1 = {
            "name": name,
            "phone": phone,
        }
        ret = await member.update_one({"id": id}, {"$set": t1})
        return {"result": 1, "updated_count": str(ret.modified_count)}
    except Exception as e:
        print(e)
        return {"result": 0, "message": str(e)}


# 로그인 => 127.0.0.1:8000u/api/member/login
# { "id": "a", "pw": "1234"}
@router.post("/login")
async def login(
    id: str = Body(...),
    pw: str = Body(...),
):
    try:
        doc = await member.find_one({"id": id})
        if not doc:
            return {"result": -1, "message": "존재하지 않는 아이디입니다."}

        if not verify_password(pw, doc["pw"]):
            return {"result": -2, "message": "비밀번호가 일치하지 않습니다."}

        acc_token = access_token.create_access_token({"id": id})
        ref_token = refresh_token.create_refresh_token({"id": id})

        return {"result": 1, "access_token": acc_token, "refresh_token": ref_token}
    except Exception as e:
        print(e)
        return {"result": 0, "message": str(e)}


# 회원가입 => 127.0.0.1:8000/api/member/join
# {"id":"a", "pw": "1234", "name": "aa", "phone":"010-1234-5678"}
@router.post("/join")
async def join(
    id: str = Body(...),
    pw: str = Body(...),
    name: str = Body(...),
    phone: str = Body(...),
):
    try:
        # 동일아이디 체크
        doc = await member.find_one({"id": id})
        if doc:
            return {"result": -1, "message": "이미 존재하는 아이디 입니다."}

        t1 = {
            "id": id,
            "pw": hash_password(pw),
            "name": name,
            "phone": phone,
            "create_at": datetime.now(),
        }
        ret = await member.insert_one(t1)

        if ret.inserted_id:
            return {"result": 1, "inserted_id": str(ret.inserted_id)}
    except Exception as e:
        print(e)
        return {"result": 0, "message": str(e)}
