"""Asynchronous AI pipeline (Celery).

``process_product_task`` orchestrates the full job for one submitted link:

    PENDING → SCRAPING → EXTRACTING → GENERATING_3D → COMPLETED
                                                    ↘ FAILED

Each stage updates the ``Product`` row so the client's status-polling endpoint
reflects live progress.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import httpx
from celery.exceptions import SoftTimeLimitExceeded

from .celery_app import celery_app
from .config import settings
from .database import SessionLocal
from .models import Product, TaskStatus
from .services.scraper import capture_product_page
from .services.tripo3d import Tripo3DClient
from .services.vision import extract_product_data

logger = logging.getLogger(__name__)


def _save_screenshot(product_id: str, content: bytes) -> str:
    """Persist the screenshot to the configured directory and return its path."""
    out_dir = Path(settings.SCREENSHOT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{product_id}.png"
    path.write_bytes(content)
    return str(path)


def _download_image(url: str) -> tuple[bytes, str]:
    """Fetch a product image; returns (bytes, mime). Raises on failure."""
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
    mime = resp.headers.get("content-type", "image/png").split(";")[0].strip()
    return resp.content, mime


@celery_app.task(bind=True, name="app.tasks.process_product_task", max_retries=0)
def process_product_task(self, product_id: str) -> dict:
    """Run scrape → vision-extract → 3D-generate for a single product row."""
    db = SessionLocal()

    def _update(**fields) -> None:
        """Patch the product row and commit immediately so polling sees progress."""
        for key, value in fields.items():
            setattr(product, key, value)
        db.add(product)
        db.commit()

    try:
        product = db.get(Product, product_id)
        if product is None:
            logger.error("Product %s not found; aborting task", product_id)
            return {"status": "missing", "product_id": product_id}

        # ── 1. Scrape ─────────────────────────────────────────────────────────
        _update(status=TaskStatus.SCRAPING, status_detail="Capturing product page")
        scrape = capture_product_page(product.source_url)
        screenshot_path = _save_screenshot(product_id, scrape.screenshot_bytes)
        _update(
            screenshot_path=screenshot_path,
            product_image_url=scrape.product_image_url,
            status_detail="Page captured",
        )

        # ── 2. Vision LLM extraction ──────────────────────────────────────────
        _update(status=TaskStatus.EXTRACTING, status_detail="Extracting product data")
        extracted = extract_product_data(
            scrape.screenshot_bytes, media_type=scrape.screenshot_mime
        )
        _update(extracted_data=extracted, status_detail="Product data extracted")

        # ── 3. Tripo3D generation ─────────────────────────────────────────────
        _update(status=TaskStatus.GENERATING_3D, status_detail="Generating 3D garment")

        # Prefer the clean product image; fall back to the full screenshot.
        if scrape.product_image_url:
            try:
                image_bytes, image_mime = _download_image(scrape.product_image_url)
            except Exception:  # noqa: BLE001 — fall back to screenshot
                logger.warning("Falling back to screenshot for Tripo3D input")
                image_bytes, image_mime = scrape.screenshot_bytes, scrape.screenshot_mime
        else:
            image_bytes, image_mime = scrape.screenshot_bytes, scrape.screenshot_mime

        tripo = Tripo3DClient()
        image_token = tripo.upload_image(image_bytes, mime=image_mime)
        tripo_task_id = tripo.create_image_to_model_task(image_token, mime=image_mime)
        _update(tripo_task_id=tripo_task_id)

        def _on_progress(pct: int) -> None:
            _update(progress=pct, status_detail=f"Generating 3D garment ({pct}%)")

        result = tripo.poll_until_complete(tripo_task_id, on_progress=_on_progress)

        # ── Done ──────────────────────────────────────────────────────────────
        _update(
            status=TaskStatus.COMPLETED,
            status_detail="Completed",
            progress=100,
            model_url=result.model_url,
            thumbnail_url=result.thumbnail_url,
            error_message=None,
        )
        return {"status": "completed", "product_id": product_id, "model_url": result.model_url}

    except SoftTimeLimitExceeded:
        logger.error("Task for product %s exceeded soft time limit", product_id)
        _fail(db, product_id, "Processing timed out")
        raise
    except Exception as exc:  # noqa: BLE001 — any stage failure marks the job failed
        logger.exception("Pipeline failed for product %s", product_id)
        _fail(db, product_id, str(exc))
        return {"status": "failed", "product_id": product_id, "error": str(exc)}
    finally:
        db.close()


def _fail(db, product_id: str, message: str) -> None:
    """Best-effort marking of a product row as FAILED."""
    try:
        product = db.get(Product, product_id)
        if product is not None:
            product.status = TaskStatus.FAILED
            product.error_message = message[:2000]
            db.add(product)
            db.commit()
    except Exception:  # noqa: BLE001 — never mask the original error
        logger.exception("Failed to persist failure state for product %s", product_id)
