# app / database.py

from motor.motor_asyncio import AsyncIOMotorClient

url = "mongodb://admin:1234@localhost:27017"
client = AsyncIOMotorClient(url)

db = client["db1"]
board = db["board"]
counter = db["counter"]
item = db["item"]

customer = db["customer"]
react_item = db["react_item"]


# 시퀀스 생성
async def get_next_sequence(name: str) -> int:
    query = {"_id": name}
    update = {"$inc": {"seq": 1}}
    ret = await counter.find_one_and_update(
        query,
        update,
        # these two options are needed if we want to create when there's no entry
        upsert=True,
        return_document=True,
    )
    return ret["seq"]
