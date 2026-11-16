def test_create_link(client):
    r = client.post("/api/links", json={"url": "https://example.com", "owner_key": "owner-123"})
    assert r.status_code == 201
    body = r.json()
    assert len(body["code"]) == 7
    assert body["short_url"].endswith(body["code"])


def test_redirect(client):
    code = client.post(
        "/api/links", json={"url": "https://example.com/x", "owner_key": "owner-123"}
    ).json()["code"]

    r = client.get(f"/{code}", follow_redirects=False)
    assert r.status_code == 302
    assert r.headers["location"] == "https://example.com/x"


def test_unknown_code(client):
    assert client.get("/yok1234", follow_redirects=False).status_code == 404


def test_delete_requires_owner(client):
    code = client.post(
        "/api/links", json={"url": "https://example.com", "owner_key": "owner-123"}
    ).json()["code"]

    assert client.delete(f"/api/links/{code}", headers={"X-Owner-Key": "baska"}).status_code == 403
    assert (
        client.delete(f"/api/links/{code}", headers={"X-Owner-Key": "owner-123"}).status_code == 204
    )
    assert client.get(f"/{code}", follow_redirects=False).status_code == 404
