"""FastAPI application entrypoint.

Run locally with:

    uvicorn app.main:app --reload

Routes (under API_V1_PREFIX, default ``/api/v1``):

    POST /products/submit             — submit a retail link (enqueues pipeline)
    GET  /products/{id}               — poll task status / result
    GET  /products                    — list recent jobs
    PUT  /users/{user_id}/dimensions  — save body dimensions
    GET  /users/{user_id}/dimensions  — fetch body dimensions
    GET  /health                      — liveness probe
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import products, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # For production, manage schema with Alembic migrations instead. create_all
    # is convenient for first-run / development and is idempotent.
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(products.router, prefix=settings.API_V1_PREFIX)
    app.include_router(users.router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.APP_NAME}

    return app


app = create_app()
