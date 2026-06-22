"""Celery application instance.

Run the worker with:

    celery -A app.celery_app.celery_app worker --loglevel=info --concurrency=2

Concurrency is kept modest because each task drives a headless Chromium instance
(Playwright) which is memory-hungry.
"""

from celery import Celery

from .config import settings

celery_app = Celery(
    "urgodoc",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # The whole pipeline (scrape + LLM + 3D generation polling) can take minutes.
    task_time_limit=900,        # hard kill after 15 min
    task_soft_time_limit=840,   # raise SoftTimeLimitExceeded at 14 min
    worker_max_tasks_per_child=20,  # recycle workers to avoid Chromium leaks
)
