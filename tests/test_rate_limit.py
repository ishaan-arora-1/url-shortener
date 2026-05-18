from httpx import AsyncClient

from app.config import get_settings


async def test_shorten_is_rate_limited(client: AsyncClient):
    settings = get_settings()

    last_status = None
    for i in range(settings.rate_limit_max + 1):
        resp = await client.post("/shorten", json={"url": f"https://example.com/r/{i}"})
        last_status = resp.status_code

    # The request that tips over the limit should be rejected.
    assert last_status == 429


async def test_requests_under_limit_pass(client: AsyncClient):
    settings = get_settings()

    for i in range(settings.rate_limit_max):
        resp = await client.post("/shorten", json={"url": f"https://example.com/ok/{i}"})
        assert resp.status_code == 201
