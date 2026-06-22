"""ORM models.

Two aggregates:

* ``Product``     — one row per submitted retail link; tracks the async pipeline
                    (scrape → vision-extract → 3D-generate) and stores results.
* ``UserProfile`` — a stylist's / shopper's body measurements, used to calibrate
                    the custom-dimension 3D avatar on the client.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class TaskStatus(str, enum.Enum):
    """Lifecycle of a single product-processing job."""

    PENDING = "PENDING"            # queued, not yet picked up by a worker
    SCRAPING = "SCRAPING"          # Playwright capturing the page
    EXTRACTING = "EXTRACTING"      # Vision LLM extracting metadata + dimensions
    GENERATING_3D = "GENERATING_3D"  # Tripo3D building the .glb
    COMPLETED = "COMPLETED"        # model_url is populated
    FAILED = "FAILED"             # see error_message


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)

    # Input
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    affiliate_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Pipeline state
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=False, length=20),
        default=TaskStatus.PENDING,
        nullable=False,
        index=True,
    )
    status_detail: Mapped[str | None] = mapped_column(String(255), nullable=True)
    progress: Mapped[int] = mapped_column(default=0)  # 0–100, driven by Tripo3D

    # Scraper output
    screenshot_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    product_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Vision LLM output — full structured payload (title, brand, price, colors,
    # material, estimated garment dimensions, etc.)
    extracted_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Tripo3D output
    tripo_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model_url: Mapped[str | None] = mapped_column(Text, nullable=True)       # .glb
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)

    # Stable identifier supplied by the client (device id, auth subject, etc.)
    user_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)

    # Core body measurements (centimetres) — calibrated via MediaPipe Holistic
    # on the device and posted here.
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    chest_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    waist_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    hips_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    inseam_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    shoulder_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    arm_length_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    neck_cm: Mapped[float | None] = mapped_column(Float, nullable=True)

    gender: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fit_preference: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Raw MediaPipe landmark dump, kept for re-derivation / debugging.
    raw_landmarks: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
