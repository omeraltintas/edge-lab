import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://edge:edge@192.168.56.10:15432/edge",
)
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:18000")
CODE_LENGTH = 7

# Cache (Faz 3)
REDIS_URL = os.getenv("REDIS_URL", "redis://192.168.56.10:16379/0")
# Varsayilan kapali: cache'siz hal "referans" kabul edilir, acmak bilincli bir karar.
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "false").lower() in {"1", "true", "yes"}
# TTL, invalidation kacagi oldugunda bayat verinin ust siniridir.
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
