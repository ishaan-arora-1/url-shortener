from httpx import AsyncClient


async def test_stats_counts_clicks(client: AsyncClient):
    code = (
        await client.post("/shorten", json={"url": "https://example.com/measured"})
    ).json()["short_code"]

    for _ in range(3):
        await client.get(f"/{code}", follow_redirects=False)

    resp = await client.get(f"/{code}/stats")
    assert resp.status_code == 200

    body = resp.json()
    assert body["short_code"] == code
    assert body["original_url"] == "https://example.com/measured"
    assert body["clicks"] == 3
    assert body["last_accessed_at"] is not None


async def test_stats_starts_at_zero(client: AsyncClient):
    code = (
        await client.post("/shorten", json={"url": "https://example.com/fresh"})
    ).json()["short_code"]

    body = (await client.get(f"/{code}/stats")).json()
    assert body["clicks"] == 0
    assert body["last_accessed_at"] is None


async def test_stats_404_for_unknown_code(client: AsyncClient):
    resp = await client.get("/nope/stats")
    assert resp.status_code == 404
