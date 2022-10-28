from decouple import config, Csv


POSTGRES_USER = config('POSTGRES_USER')
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')
POSTGRES_DB = config('POSTGRES_DB')
POSTGRES_HOST = config('POSTGRES_HOST', default='localhost')
POSTGRES_PORT = config('POSTGRES_PORT', cast=int, default=5432)

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@" \
               f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


REDIS_HOST = config('REDIS_HOST')
REDIS_PORT = config('REDIS_PORT', cast=int)
REDIS_DB = config('REDIS_DB', cast=int)

REDIS_URL = f"redis://{REDIS_HOST}"


SERVER_URL = config('SERVER_URL')
SERVER_HOST = config('SERVER_HOST', default='localhost')
SERVER_PORT = config('SERVER_PORT', cast=int)

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())

APP_NAME = 'Quiz'

# OAuth
SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int)

# Auth0
DOMAIN = config('DOMAIN')
API_AUDIENCE = config('API_AUDIENCE')
ALGORITHMS = config('ALGORITHMS')
ISSUER = f"https://{DOMAIN}/"


