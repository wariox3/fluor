from decouple import config

DEBUG=config("DEBUG", default=False, cast=bool)

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

B2_KEY_ID = config("B2_KEY_ID", default="")
B2_APPLICATION_KEY = config("B2_APPLICATION_KEY", default="")
B2_BUCKET_NAME = config("B2_BUCKET_NAME", default="")

DEFAULT_EMPRESA_ID = 1

APP_URL = config("APP_URL", default="http://localhost:4200")

