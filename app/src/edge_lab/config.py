import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://edge:edge@192.168.56.10:15432/edge",
)
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:18000")
CODE_LENGTH = 7
