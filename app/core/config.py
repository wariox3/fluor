import os

SECRET_KEY = os.getenv("SECRET_KEY", "cambia_esto_en_produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60