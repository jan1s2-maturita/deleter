from typing import Annotated
from fastapi import FastAPI, Cookie, Header
import redis
from .config import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_USER, REDIS_PASSWORD, PUBLIC_KEY_PATH, KUBERNETES_KEY, KUBERNETES_URL, DEPLOY_NAMESPACE
from jwt import decode
from pydantic import BaseModel
from kubernetes import client, config

app = FastAPI()

def get_k8s_config():
    configuration = client.Configuration()
    configuration.api_key['authorization'] = KUBERNETES_KEY
    configuration.api_key_prefix['authorization'] = 'Bearer'
    configuration.host = KUBERNETES_URL
    configuration.verify_ssl = False

    v1 = client.CoreV1Api(client.ApiClient(configuration))
    return v1
v1 = get_k8s_config()


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, username=REDIS_USER, password=REDIS_PASSWORD)

def delete_in_redis(user_id, image_id):

    # remove image_id from redis zset of user id
    r.srem(user_id, image_id)

def delete_in_k8s(user_id, image_id):
    # delete the image from k8s
    v1.delete_namespaced_pod(image_id, namespace=user_id)


@app.delete("/delete/{image_id}")
def delete_deploy(deploy_name: int, x_token: Annotated[str, Header()]):
    try:
        payload = decode(x_token, PUBLIC_KEY_PATH, algorithms=['RS256'])
    except Exception as e:
        return {"error": "token is invalid"}


    delete_in_redis(payload["id"],deploy_name)
    delete_in_k8s(payload["id"],deploy_name)

    return {"message": "delete successfully"}
