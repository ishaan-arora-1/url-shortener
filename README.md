# URL Shortener

A small, fast URL shortener built with **FastAPI**, **PostgreSQL** and **Redis**.

Shorten a long URL into a compact base62 code, redirect through it, and track how
often each link gets hit. Hot redirects are served from Redis so they don't touch
the database, the shorten endpoint is IP rate limited, and the whole request path is
async end to end.

[![CI](https://github.com/ishaan-arora-1/url-shortener/actions/workflows/ci.yml/badge.svg)](https://github.com/ishaan-arora-1/url-shortener/actions/workflows/ci.yml)

---

## How it works

```mermaid
flowchart LR
    Client -->|POST /shorten| API[FastAPI]
    Client -->|GET /:code| API

    API -->|cache hit| Redis[(Redis)]
    API -->|cache miss / writes| PG[(PostgreSQL)]
    Redis -. fills on miss .- PG

    subgraph Async
      API
    end
```

- **`POST /shorten`** writes the mapping to Postgres. The short code is the row id
  (offset a little) run through base62, so codes are unique without any collision
  checks. Re-shortening a URL we've already seen returns the same code.
- **`GET /{code}`** looks in Redis first. On a miss it reads Postgres and back-fills
  the cache, so repeat hits skip the DB entirely. The click counter is bumped in a
  background task *after* the redirect is sent, so analytics never add latency.
- **Rate limiting** is a fixed-window counter in Redis, keyed by client IP.

## Tech stack

| Layer       | Choice                          |
|-------------|---------------------------------|
| API         | FastAPI (async)                 |
| Database    | PostgreSQL via SQLAlchemy 2.0 (async) |
| Migrations  | Alembic                         |
| Cache / rate limit | Redis (`redis.asyncio`)  |
| Validation  | Pydantic v2                     |
| Tests       | pytest + httpx + fakeredis      |
| Packaging   | Docker + docker-compose         |

## API

| Method | Path              | Description                                   |
|--------|-------------------|-----------------------------------------------|
| POST   | `/shorten`        | Create a short code for a URL (rate limited)  |
| GET    | `/{code}`         | 307 redirect to the original URL              |
| GET    | `/{code}/stats`   | Click count + timestamps for a code           |
| GET    | `/health`         | Liveness check                                |

Interactive docs are served at `/docs` (Swagger) and `/redoc`.

### Examples

```bash
# Shorten
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/some/really/long/path"}'
# -> {"short_code":"4c92","short_url":"http://localhost:8000/4c92","original_url":"..."}

# Redirect (follow it)
curl -L http://localhost:8000/4c92

# Stats
curl http://localhost:8000/4c92/stats
# -> {"short_code":"4c92","original_url":"...","clicks":1,"created_at":"...","last_accessed_at":"..."}
```

## Running locally

The fastest path is docker-compose, which brings up the API, Postgres and Redis and
runs migrations on boot:

```bash
cp .env.example .env       # optional, compose sets sane defaults
docker compose up --build
```

The API is then on http://localhost:8000 (try http://localhost:8000/docs).

### Without Docker

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# point these at a local Postgres + Redis
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/urlshortener
export REDIS_URL=redis://localhost:6379/0

alembic upgrade head
uvicorn app.main:app --reload
```

## Configuration

All config comes from the environment (or a `.env` file). See `.env.example`.

| Variable            | Default                          | Purpose                                  |
|---------------------|----------------------------------|------------------------------------------|
| `DATABASE_URL`      | local Postgres                   | Async SQLAlchemy connection string       |
| `REDIS_URL`         | `redis://localhost:6379/0`       | Redis connection string                  |
| `BASE_URL`          | `http://localhost:8000`          | Used to build the returned `short_url`   |
| `CACHE_TTL`         | `3600`                           | Seconds a resolved code stays cached     |
| `RATE_LIMIT_MAX`    | `20`                             | Max `/shorten` requests per window per IP|
| `RATE_LIMIT_WINDOW` | `60`                             | Rate-limit window in seconds             |
| `ID_OFFSET`         | `1000000`                        | Offset before base62 so codes aren't tiny|

## Tests

Tests run against an in-memory SQLite DB and a fake Redis, so there's nothing to spin
up — just:

```bash
pip install -r requirements-dev.txt
pytest
```

CI runs `ruff` + `pytest` on every push and PR (see `.github/workflows/ci.yml`).

## Project layout

```
app/
  main.py        # routes: shorten, redirect, stats, health
  crud.py        # db operations
  cache.py       # redis client
  rate_limit.py  # ip rate-limit dependency
  shortcode.py   # base62 encode/decode
  models.py      # SQLAlchemy model
  schemas.py     # pydantic request/response models
  config.py      # settings
  database.py    # async engine + session
alembic/         # migrations
tests/           # pytest suite
```
