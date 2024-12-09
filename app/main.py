from typing import Annotated
from fastapi import FastAPI, Header
from .config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_USER, REDIS_PASSWORD, PUBLIC_KEY_PATH, KUBERNETES_KEY, KUBERNETES_URL
from jwt import decode
from .models.k8s_helper import Kubernetes
from .models.redis_helper import RedisConnector

app = FastAPI()
kube = Kubernetes(key=KUBERNETES_KEY, url=KUBERNETES_URL)
r = RedisConnector(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD, user=REDIS_USER)




def delete_in_redis(user_id, image_id):

    # remove image_id from redis zset of user id
    r.delete_instance(user_id, image_id)

def delete_in_k8s(user_id, image_id):
    # delete the image from k8s
    kube.delete_deploy(user_id, image_id)


@app.delete("/delete/{image_id}")
def delete_deploy(deploy_name: int, x_token: Annotated[str, Header()]):
    try:
        payload = decode(x_token, PUBLIC_KEY_PATH, algorithms=['RS256'])
    except Exception as e:
        return {"error": "token is invalid"}


    delete_in_redis(payload["id"],deploy_name)
    delete_in_k8s(payload["id"],deploy_name)

    return {"message": "delete successfully"}
