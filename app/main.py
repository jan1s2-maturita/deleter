from fastapi import FastAPI, Cookie
import redis
from .config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_USER, REDIS_PASSWORD, PUBLIC_KEY_PATH
from jwt import decode
from pydantic import BaseModel

app = FastAPI()


def delete_in_redis(user_id, image_id):
    assert (REDIS_HOST and REDIS_PORT and REDIS_DB and REDIS_USER and REDIS_PASSWORD)
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, username=REDIS_USER, password=REDIS_PASSWORD)

    # remove image_id from redis zset of user id
    r.srem(user_id, image_id)

class Image(BaseModel):
    user_id: str
    image_id: str

# jwt in cookie, rest in body, deletes
@app.delete("/delete")
async def delete_image(image: Image, token: str = Cookie(None)):
    try:
        payload = decode(token, PUBLIC_KEY_PATH, algorithms=['RS256'])
    except Exception as e:
        return {"error": str(e)}

    if payload['id'] != image.user_id:
        return {"error": "user_id in token and body not match"}

    delete_in_redis(image.user_id, image.image_id)
    return {"message": "delete successfully"}
