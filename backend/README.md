# UrgoDoc — Fashion 3D Try-On Backend

FastAPI + Celery backend for a cross-platform virtual try-on app. A stylist pastes
**any** e-commerce retail link; the backend scrapes it, extracts product metadata
and technical garment dimensions with a Vision LLM, generates a 3D garment
(`.glb`) via Tripo3D, and exposes everything to the React Native (Expo) client —
which renders the garment on a custom-dimension avatar with Three.js
(`@react-three/fiber`).

Every submitted link is also rewritten into an **affiliate** link for automated
monetization.

## Architecture

```
React Native (Expo) client
        │  POST /products/submit  { url }
        ▼
┌──────────────────┐      enqueue       ┌──────────────────────────────┐
│   FastAPI (API)  │ ─────────────────► │   Celery worker (tasks.py)   │
│   main.py        │                    │                              │
│   - submit       │   poll status      │  1. Playwright screenshot    │
│   - status       │ ◄───────────────── │  2. Claude Vision → JSON     │
│   - dimensions   │                    │  3. Tripo3D image → .glb     │
└────────┬─────────┘                    └──────────────┬───────────────┘
         │                                             │
         ▼                                             ▼
   PostgreSQL  ◄──────────── shared models ──────────► Redis (broker/result)
```

| Concern            | Tech                                                   |
| ------------------ | ----------------------------------------------------- |
| API                | FastAPI                                               |
| DB                 | PostgreSQL + SQLAlchemy 2.0                           |
| Async task queue   | Celery + Redis                                        |
| Scraping           | Playwright (headless Chromium) + residential proxy    |
| Data extraction    | Anthropic Claude Vision (`claude-opus-4-8`), Structured Outputs |
| 2D → 3D            | Tripo3D OpenAPI (`image_to_model`)                    |
| Monetization       | Skimlinks / Sovrn deep links, Amazon Associates       |

> The original spec mentioned "Claude 3.5 Sonnet"; that alias is outdated, so the
> code defaults to the current `claude-opus-4-8`. To use a cheaper tier for
> high-volume extraction set `VISION_MODEL=claude-haiku-4-5`. To swap to OpenAI
> GPT-4o-mini instead, reimplement `app/services/vision.py` against that SDK —
> the rest of the pipeline is provider-agnostic.

## Layout

```
backend/
├── app/
│   ├── main.py            # FastAPI app + routes wiring
│   ├── config.py          # env-driven settings
│   ├── database.py        # SQLAlchemy engine/session
│   ├── models.py          # Product, UserProfile, TaskStatus
│   ├── schemas.py         # Pydantic request/response models
│   ├── celery_app.py      # Celery instance
│   ├── tasks.py           # the async AI pipeline
│   ├── routers/
│   │   ├── products.py     # submit / status / list
│   │   └── users.py        # body-dimension upsert/fetch
│   └── services/
│       ├── scraper.py      # Playwright capture
│       ├── vision.py       # Claude Vision extraction
│       ├── tripo3d.py      # Tripo3D client
│       └── affiliate.py    # affiliate-link rewriting
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Quick start (Docker)

```bash
cd backend
cp .env.example .env          # fill in ANTHROPIC_API_KEY and TRIPO3D_API_KEY
docker compose up --build
```

API is then at `http://localhost:8000` (interactive docs at `/docs`).

## Quick start (local)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env          # fill in keys + point at local Postgres/Redis

# terminal 1 — API
uvicorn app.main:app --reload

# terminal 2 — worker
celery -A app.celery_app.celery_app worker --loglevel=info --concurrency=2
```

## API

| Method | Path                                  | Description                          |
| ------ | ------------------------------------- | ------------------------------------ |
| POST   | `/api/v1/products/submit`             | Submit a retail link → `202` + job id |
| GET    | `/api/v1/products/{id}`               | Poll job status / result             |
| GET    | `/api/v1/products`                    | List recent jobs                     |
| PUT    | `/api/v1/users/{user_id}/dimensions`  | Upsert body measurements             |
| GET    | `/api/v1/users/{user_id}/dimensions`  | Fetch body measurements              |
| GET    | `/health`                             | Liveness probe                       |

### Example

```bash
# 1. Submit
curl -X POST http://localhost:8000/api/v1/products/submit \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example-retailer.com/products/linen-shirt"}'
# → {"id": "…", "status": "PENDING", "affiliate_url": "…", ...}

# 2. Poll until status == "COMPLETED"
curl http://localhost:8000/api/v1/products/<id>
# → {"status": "COMPLETED", "model_url": "https://…/model.glb",
#    "extracted_data": { "title": "...", "estimated_dimensions_cm": {...} }, ... }

# 3. Save the user's calibrated measurements (from MediaPipe on-device)
curl -X PUT http://localhost:8000/api/v1/users/device-abc/dimensions \
  -H "Content-Type: application/json" \
  -d '{"height_cm": 178, "chest_cm": 98, "waist_cm": 82, "inseam_cm": 81}'
```

## Job lifecycle

`PENDING → SCRAPING → EXTRACTING → GENERATING_3D → COMPLETED` (or `FAILED`, with
`error_message`). `progress` (0–100) tracks the Tripo3D generation stage so the
client can show a live progress bar.

## Production notes

- Replace `Base.metadata.create_all` with **Alembic** migrations.
- Serve large screenshots / `.glb` files from object storage (S3/GCS) and store
  only URLs in the DB; `model_url` already points at Tripo3D's hosted asset.
- Configure `SCRAPER_PROXY_SERVER` with a residential proxy for resilient
  scraping of bot-protected retailers.
- Run multiple workers behind the same Redis broker to scale throughput.
