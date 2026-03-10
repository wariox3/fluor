from decouple import config

DEBUG=config("DEBUG", default=False, cast=bool)

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

