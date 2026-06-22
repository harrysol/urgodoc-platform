"""Pydantic request/response schemas (API contract).

``protected_namespaces=()`` is set on responses that expose a ``model_url``
field, otherwise Pydantic v2 warns about the ``model_`` prefix colliding with
its reserved namespace.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from .models import TaskStatus

# ── Products ──────────────────────────────────────────────────────────────────


class ProductSubmitRequest(BaseModel):
    """Body for POST /products/submit — a single retail link to process."""

    url: HttpUrl


class ProductTaskResponse(BaseModel):
    """Lightweight acknowledgement returned when a job is enqueued."""

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    status: TaskStatus
    source_url: str
    affiliate_url: str | None = None
    created_at: datetime


class ProductDetailResponse(ProductTaskResponse):
    """Full job state returned by the status-polling endpoint."""

    status_detail: str | None = None
    progress: int = 0
    product_image_url: str | None = None
    extracted_data: dict[str, Any] | None = None
    tripo_task_id: str | None = None
    model_url: str | None = None
    thumbnail_url: str | None = None
    error_message: str | None = None
    updated_at: datetime


# ── User dimensions ───────────────────────────────────────────────────────────


class UserDimensionsRequest(BaseModel):
    """Body for PUT /users/{user_id}/dimensions (upsert)."""

    height_cm: float | None = Field(default=None, gt=0, lt=300)
    weight_kg: float | None = Field(default=None, gt=0, lt=500)
    chest_cm: float | None = Field(default=None, gt=0, lt=300)
    waist_cm: float | None = Field(default=None, gt=0, lt=300)
    hips_cm: float | None = Field(default=None, gt=0, lt=300)
    inseam_cm: float | None = Field(default=None, gt=0, lt=200)
    shoulder_cm: float | None = Field(default=None, gt=0, lt=150)
    arm_length_cm: float | None = Field(default=None, gt=0, lt=150)
    neck_cm: float | None = Field(default=None, gt=0, lt=100)
    gender: str | None = None
    fit_preference: str | None = None
    raw_landmarks: dict[str, Any] | None = None


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    height_cm: float | None = None
    weight_kg: float | None = None
    chest_cm: float | None = None
    waist_cm: float | None = None
    hips_cm: float | None = None
    inseam_cm: float | None = None
    shoulder_cm: float | None = None
    arm_length_cm: float | None = None
    neck_cm: float | None = None
    gender: str | None = None
    fit_preference: str | None = None
    created_at: datetime
    updated_at: datetime
