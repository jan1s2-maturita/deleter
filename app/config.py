import os
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))
REDIS_USER = os.environ.get('REDIS_USER', 'user')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', 'password')
PUBLIC_KEY_PATH = os.environ.get('PUBLIC_KEY_PATH', 'public.pem')
