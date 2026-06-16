from decouple import config

DEBUG=config("DEBUG", default=False, cast=bool)

# Observabilidad / Sentry. Si SENTRY_DSN está vacío, Sentry queda desactivado.
SENTRY_DSN = config("SENTRY_DSN", default="")
ENVIRONMENT = config("ENVIRONMENT", default="production")
SENTRY_TRACES_SAMPLE_RATE = config("SENTRY_TRACES_SAMPLE_RATE", default=0.0, cast=float)

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

B2_KEY_ID = config("B2_KEY_ID", default="")
B2_APPLICATION_KEY = config("B2_APPLICATION_KEY", default="")
B2_BUCKET_NAME = config("B2_BUCKET_NAME", default="")

DEFAULT_EMPRESA_ID = 1

APP_URL = config("APP_URL", default="http://localhost:4200")

# Zona horaria fijada en cada conexión MySQL (Colombia, sin horario de verano).
# Así NOW()/CURRENT_TIMESTAMP y los server_default producen hora local.
DB_TIME_ZONE = config("DB_TIME_ZONE", default="-05:00")

ZINC_URL = config("ZINC_URL", default="http://zinc.semantica.com.co")

TURNSTILE_SECRET_KEY = config("TURNSTILE_SECRET_KEY", default="")
TURNSTILE_ENABLED = config("TURNSTILE_ENABLED", default=True, cast=bool)

