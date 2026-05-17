import pytest
from httpx import AsyncClient


async def test_shorten_returns_code_and_url(client: AsyncClient):
    resp = await client.post("/shorten", json={"url": "https://example.com/some/long/path"})

    assert resp.status_code == 201
    body = resp.json()
    assert body["short_code"]
    assert body["original_url"] == "https://example.com/some/long/path"
    assert body["short_url"].endswith(body["short_code"])


async def test_shorten_is_idempotent_for_same_url(client: AsyncClient):
    first = await client.post("/shorten", json={"url": "https://example.com/page"})
    second = await client.post("/shorten", json={"url": "https://example.com/page"})

    assert first.json()["short_code"] == second.json()["short_code"]


async def test_shorten_rejects_invalid_url(client: AsyncClient):
    resp = await client.post("/shorten", json={"url": "not-a-real-url"})
    assert resp.status_code == 422


@pytest.mark.parametrize("n", [3])
async def test_distinct_urls_get_distinct_codes(client: AsyncClient, n: int):
    codes = set()
    for i in range(n):
        resp = await client.post("/shorten", json={"url": f"https://example.com/{i}"})
        codes.add(resp.json()["short_code"])
    assert len(codes) == n
