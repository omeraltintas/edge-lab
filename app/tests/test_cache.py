"""Cache-aside davranisi.

Redis'i calistirmadan test ediyoruz: `edge_lab.cache` fonksiyonlarini taklit
ediyoruz. Boylece testler SQLite + TestClient ile, dis servis olmadan kosar.
"""

from edge_lab import cache


def test_redirect_served_from_cache(client, monkeypatch):
    # DB'de olmayan bir kod: cevap yalnizca cache'ten gelebilir.
    monkeypatch.setattr(cache, "get_url", lambda code: "https://cached.example/x")

    r = client.get("/cachede", follow_redirects=False)

    assert r.status_code == 302
    assert r.headers["location"] == "https://cached.example/x"


def test_cache_miss_falls_back_to_db(client, monkeypatch):
    written = []
    monkeypatch.setattr(cache, "get_url", lambda code: None)
    monkeypatch.setattr(cache, "set_url", lambda code, url: written.append((code, url)))

    code = client.post(
        "/api/links", json={"url": "https://example.com/db", "owner_key": "owner-123"}
    ).json()["code"]

    r = client.get(f"/{code}", follow_redirects=False)

    assert r.status_code == 302
    assert r.headers["location"] == "https://example.com/db"
    assert written == [(code, "https://example.com/db")]


def test_delete_invalidates_cache_key(client, monkeypatch):
    dropped = []
    monkeypatch.setattr(cache, "get_url", lambda code: None)
    monkeypatch.setattr(cache, "set_url", lambda code, url: None)
    monkeypatch.setattr(cache, "drop", lambda code: dropped.append(code))

    code = client.post(
        "/api/links", json={"url": "https://example.com/sil", "owner_key": "owner-123"}
    ).json()["code"]

    assert (
        client.delete(f"/api/links/{code}", headers={"X-Owner-Key": "owner-123"}).status_code == 204
    )
    assert dropped == [code]


def test_cache_disabled_means_no_redis_call(monkeypatch):
    # CACHE_ENABLED kapaliyken fonksiyonlar hicbir sey yapmamali; Redis
    # istemcisine dokunuldugunu gostermek icin patlatilan bir istemci koyuyoruz.
    class PatlayanIstemci:
        def get(self, *_args, **_kwargs):
            raise AssertionError("cache kapaliyken redis'e gidilmemeli")

        set = get
        delete = get

    monkeypatch.setattr(cache, "CACHE_ENABLED", False)
    monkeypatch.setattr(cache, "_client", PatlayanIstemci())

    assert cache.get_url("hotlink") is None
    cache.set_url("hotlink", "https://example.com")
    cache.drop("hotlink")
