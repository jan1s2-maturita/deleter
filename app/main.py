from fastapi import FastAPI
import redis
from .config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_USER, REDIS_PASSWORD

app = FastAPI()

def delete_in_redis(user_id, image_id):
    assert (REDIS_HOST and REDIS_PORT and REDIS_DB and REDIS_USER and REDIS_PASSWORD)
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, username=REDIS_USER, password=REDIS_PASSWORD)

    # remove image_id from redis zset of user id
    r.srem(user_id, image_id)
