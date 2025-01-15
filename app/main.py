from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, HTTPException, Header
from .config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_USER, REDIS_PASSWORD, PUBLIC_KEY_PATH, KUBERNETES_KEY, KUBERNETES_URL
from jwt import decode
from .models.k8s_helper import Kubernetes
from .models.redis_helper import RedisConnector

kube: Kubernetes
r: RedisConnector

@asynccontextmanager
async def init(app: FastAPI):
    global kube
    global r
    kube = Kubernetes(key=KUBERNETES_KEY, url=KUBERNETES_URL)
    r = RedisConnector(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD, user=REDIS_USER)
    yield

app = FastAPI(lifespan=init,
              root_path="/api/deployer")
# kube = Kubernetes(key=KUBERNETES_KEY, url=KUBERNETES_URL)
# r = RedisConnector(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD, user=REDIS_USER)

def delete_in_redis(user_id, image_id):

    # remove image_id from redis zset of user id
    r.delete_instance(user_id, image_id)

def delete_in_k8s(user_id, image_id):
    # delete the image from k8s
    kube.delete_deploy(user_id, image_id)


@app.delete("/{challenge_id}")
def delete_deploy(challenge_id: int, x_token: Annotated[str, Header()]):
    payload = None
    try:
        with open(PUBLIC_KEY_PATH, 'r') as f:
            public_key = f.read()
            payload = decode(x_token, public_key, algorithms=['RS256'])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


    delete_in_redis(payload["sub"],challenge_id)
    delete_in_k8s(payload["sub"],challenge_id)

    return {"message": "delete successfully"}

@app.get("/health")
def health():
    return {"message": "ok"}
