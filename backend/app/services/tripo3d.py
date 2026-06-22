"""Tripo3D client — 2D product image → downloadable ``.glb`` model.

Three-step flow against the Tripo3D OpenAPI:

  1. ``POST /upload``          → exchange image bytes for an ``image_token``
  2. ``POST /task``            → start an ``image_to_model`` job, get a ``task_id``
  3. ``GET  /task/{task_id}``  → poll until ``success`` / ``failed``

All calls are synchronous (httpx) because this runs inside a Celery worker.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass

import httpx

from ..config import settings

logger = logging.getLogger(__name__)

# Image extensions Tripo3D accepts, keyed for its ``file.type`` field.
_SUPPORTED_EXTS = {"jpg", "jpeg", "png", "webp"}


@dataclass
class Tripo3DResult:
    model_url: str          # downloadable .glb
    thumbnail_url: str | None
    task_id: str


class Tripo3DError(RuntimeError):
    """Raised on any Tripo3D API failure (HTTP, business error, or job failure)."""


class Tripo3DClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or settings.TRIPO3D_API_KEY
        self.base_url = (base_url or settings.TRIPO3D_BASE_URL).rstrip("/")
        if not self.api_key:
            raise Tripo3DError("TRIPO3D_API_KEY is not configured")

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    @staticmethod
    def _ext_from_mime(mime: str) -> str:
        ext = mime.split("/")[-1].lower()
        ext = "jpg" if ext == "jpeg" else ext
        return ext if ext in _SUPPORTED_EXTS else "png"

    def upload_image(self, content: bytes, mime: str = "image/png") -> str:
        """Upload raw image bytes and return Tripo3D's ``image_token``."""
        ext = self._ext_from_mime(mime)
        files = {"file": (f"product.{ext}", content, mime)}
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                f"{self.base_url}/upload", headers=self._headers, files=files
            )
        return self._unwrap(resp, "image upload")["image_token"]

    def create_image_to_model_task(self, image_token: str, mime: str = "image/png") -> str:
        """Start an image-to-3D job and return its ``task_id``."""
        payload = {
            "type": "image_to_model",
            "file": {"type": self._ext_from_mime(mime), "file_token": image_token},
            # Generate PBR materials so the garment renders realistically on the
            # avatar in @react-three/fiber.
            "texture": True,
            "pbr": True,
        }
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                f"{self.base_url}/task",
                headers={**self._headers, "Content-Type": "application/json"},
                json=payload,
            )
        return self._unwrap(resp, "task creation")["task_id"]

    def get_task(self, task_id: str) -> dict:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(f"{self.base_url}/task/{task_id}", headers=self._headers)
        return self._unwrap(resp, "task status")

    def poll_until_complete(
        self,
        task_id: str,
        on_progress: Callable[[int], None] | None = None,
    ) -> Tripo3DResult:
        """Block until the job succeeds, fails, or the configured timeout elapses."""
        deadline = time.monotonic() + settings.TRIPO3D_POLL_TIMEOUT
        while time.monotonic() < deadline:
            data = self.get_task(task_id)
            status = data.get("status")
            progress = int(data.get("progress", 0) or 0)
            if on_progress:
                on_progress(progress)

            if status == "success":
                output = data.get("output", {}) or {}
                # Prefer the textured PBR model; fall back to the base model.
                model_url = output.get("pbr_model") or output.get("model")
                if not model_url:
                    raise Tripo3DError("Tripo3D reported success but returned no model URL")
                return Tripo3DResult(
                    model_url=model_url,
                    thumbnail_url=output.get("rendered_image"),
                    task_id=task_id,
                )
            if status in {"failed", "banned", "expired", "cancelled", "unknown"}:
                raise Tripo3DError(f"Tripo3D task {task_id} ended with status '{status}'")

            time.sleep(settings.TRIPO3D_POLL_INTERVAL)

        raise Tripo3DError(f"Tripo3D task {task_id} timed out after "
                           f"{settings.TRIPO3D_POLL_TIMEOUT}s")

    @staticmethod
    def _unwrap(resp: httpx.Response, action: str) -> dict:
        """Validate the HTTP response and unwrap Tripo3D's ``{code, data}`` envelope."""
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise Tripo3DError(f"Tripo3D {action} HTTP {resp.status_code}: {resp.text}") from exc
        body = resp.json()
        if body.get("code") != 0:
            raise Tripo3DError(f"Tripo3D {action} error: {body}")
        return body.get("data", {})
