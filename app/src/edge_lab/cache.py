"""Cache-aside (lazy loading) icin Redis istemcisi.

Kural: cache asla istegi oldurmez.

- Redis yoksa, yavassa veya hata donduruyorsa sessizce veritabanina duseriz.
- Bu yuzden /readyz Redis'e bakmaz: cache coktugunde uc replica birden
  "hazir degil" olursa, kolayca kurtulacak bir sorun tum sistemi durdurur.
- Baglanti ilk istekte kurulur; Redis ayakta degilken uygulama yine acilir.

`CACHE_ENABLED=false` iken hicbir Redis cagrisi yapilmaz. Ayni oturumda
cache'li/cache'siz A/B kosabilmek icin var (bkz. Makefile: cache-on/cache-off).
"""

import logging

from redis import Redis
from redis.exceptions import RedisError

from edge_lab.config import CACHE_ENABLED, CACHE_TTL, REDIS_URL

log = logging.getLogger(__name__)

_client: Redis | None = None
_warned = False


def _get_client() -> Redis:
    global _client
    if _client is None:
        _client = Redis.from_url(
            REDIS_URL,
            decode_responses=True,
            # Redis yavassa istegi bekletmeyiz: 50 ms sonra DB'ye duseriz.
            socket_connect_timeout=0.05,
            socket_timeout=0.05,
        )
    return _client


def _warn_once(exc: Exception) -> None:
    # Redis coktugunde istek basina log yazmak CPU yakar; bir kez uyaririz.
    global _warned
    if not _warned:
        _warned = True
        log.warning("redis kullanilamiyor, db'ye dusuluyor: %s", exc)


def _key(code: str) -> str:
    return f"link:{code}"


def get_url(code: str) -> str | None:
    """Cache hit ise hedef URL, aksi halde None."""
    if not CACHE_ENABLED:
        return None
    try:
        return _get_client().get(_key(code))
    except RedisError as exc:
        _warn_once(exc)
        return None


def set_url(code: str, url: str) -> None:
    if not CACHE_ENABLED:
        return
    try:
        _get_client().set(_key(code), url, ex=CACHE_TTL)
    except RedisError as exc:
        _warn_once(exc)


def drop(code: str) -> None:
    if not CACHE_ENABLED:
        return
    try:
        _get_client().delete(_key(code))
    except RedisError as exc:
        _warn_once(exc)
