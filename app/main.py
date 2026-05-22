# 파일명 : app / main.py

from fastapi import FastAPI
from app.routers import board, member, item, fish

app = FastAPI()

app.include_router(board.router)
app.include_router(member.router)
app.include_router(item.router)
app.include_router(fish.router)
