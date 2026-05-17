from httpx import AsyncClient


async def test_redirect_sends_to_original(client: AsyncClient):
    code = (
        await client.post("/shorten", json={"url": "https://example.com/target"})
    ).json()["short_code"]

    resp = await client.get(f"/{code}", follow_redirects=False)

    assert resp.status_code == 307
    assert resp.headers["location"] == "https://example.com/target"


async def test_unknown_code_returns_404(client: AsyncClient):
    resp = await client.get("/doesnotexist", follow_redirects=False)
    assert resp.status_code == 404


async def test_redirect_works_on_repeat_for_cache_path(client: AsyncClient):
    code = (
        await client.post("/shorten", json={"url": "https://example.com/cached"})
    ).json()["short_code"]

    # First hit warms the cache, second should be served from Redis.
    first = await client.get(f"/{code}", follow_redirects=False)
    second = await client.get(f"/{code}", follow_redirects=False)

    assert first.headers["location"] == second.headers["location"] == "https://example.com/cached"
