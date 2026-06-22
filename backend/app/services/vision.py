"""Vision LLM extraction (Anthropic Claude).

Takes the scraped product screenshot and returns a structured JSON payload of
e-commerce metadata plus *estimated* technical garment dimensions. Structured
Outputs (``output_config.format``) guarantees the response validates against the
schema, so the caller never has to defensively parse free-form text.

The spec referenced "Claude 3.5 Sonnet"; that alias is outdated, so we default
to the current ``claude-opus-4-8``. Swap ``VISION_MODEL`` for a cheaper tier
(e.g. ``claude-haiku-4-5``) for high-volume extraction if desired.
"""

from __future__ import annotations

import base64
import json
import logging
from typing import Any

from anthropic import Anthropic

from ..config import settings

logger = logging.getLogger(__name__)

_client: Anthropic | None = None


def _get_client() -> Anthropic:
    """Lazily construct a module-level Anthropic client."""
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


# JSON Schema for Structured Outputs. Every property is listed in ``required``
# and nullable fields use ``["type", "null"]`` (Structured Outputs forbids
# leaving properties out of ``required`` and forbids unconstrained
# ``additionalProperties``).
_DIMENSIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "chest_width_cm": {"type": ["number", "null"]},
        "garment_length_cm": {"type": ["number", "null"]},
        "sleeve_length_cm": {"type": ["number", "null"]},
        "shoulder_width_cm": {"type": ["number", "null"]},
        "waist_cm": {"type": ["number", "null"]},
        "hip_cm": {"type": ["number", "null"]},
        "inseam_cm": {"type": ["number", "null"]},
    },
    "required": [
        "chest_width_cm",
        "garment_length_cm",
        "sleeve_length_cm",
        "shoulder_width_cm",
        "waist_cm",
        "hip_cm",
        "inseam_cm",
    ],
    "additionalProperties": False,
}

_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "brand": {"type": ["string", "null"]},
        "category": {"type": "string"},          # e.g. top, dress, trousers, outerwear
        "garment_type": {"type": ["string", "null"]},
        "price": {"type": ["number", "null"]},
        "currency": {"type": ["string", "null"]},
        "primary_color": {"type": ["string", "null"]},
        "colors": {"type": "array", "items": {"type": "string"}},
        "material": {"type": ["string", "null"]},
        "pattern": {"type": ["string", "null"]},
        "description": {"type": ["string", "null"]},
        "size_options": {"type": "array", "items": {"type": "string"}},
        "estimated_dimensions_cm": _DIMENSIONS_SCHEMA,
        "fit": {"type": ["string", "null"]},
        "confidence": {"type": "number"},        # 0–1, the model's own confidence
    },
    "required": [
        "title",
        "brand",
        "category",
        "garment_type",
        "price",
        "currency",
        "primary_color",
        "colors",
        "material",
        "pattern",
        "description",
        "size_options",
        "estimated_dimensions_cm",
        "fit",
        "confidence",
    ],
    "additionalProperties": False,
}

_SYSTEM_PROMPT = (
    "You are a fashion product data extraction engine for a virtual try-on "
    "platform. You receive a screenshot of an e-commerce product page and return "
    "structured data about the single primary garment shown. Read every visible "
    "price, size chart, material and measurement. For physical garment "
    "dimensions, transcribe any size-chart numbers you can read; where the page "
    "gives no explicit measurement, infer a realistic estimate for the stated "
    "size/category and lower your overall confidence accordingly. Use null for a "
    "field only when you genuinely cannot determine it. All dimensions are in "
    "centimetres."
)

_USER_PROMPT = (
    "Extract the product metadata and technical garment dimensions from this "
    "product page screenshot."
)


class VisionExtractionError(RuntimeError):
    """Raised when the Vision LLM call fails or returns unparseable output."""


def extract_product_data(image_bytes: bytes, media_type: str = "image/png") -> dict[str, Any]:
    """Run the Vision LLM over a product screenshot and return structured data."""
    if not settings.ANTHROPIC_API_KEY:
        raise VisionExtractionError("ANTHROPIC_API_KEY is not configured")

    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    try:
        response = _get_client().messages.create(
            model=settings.VISION_MODEL,
            max_tokens=2048,
            thinking={"type": "adaptive"},  # let Claude reason about measurements
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": b64,
                            },
                        },
                        {"type": "text", "text": _USER_PROMPT},
                    ],
                }
            ],
            output_config={
                "format": {"type": "json_schema", "schema": _EXTRACTION_SCHEMA}
            },
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Vision LLM request failed")
        raise VisionExtractionError(f"Vision LLM request failed: {exc}") from exc

    if response.stop_reason == "refusal":
        raise VisionExtractionError("Vision LLM refused to process the image")

    # Structured Outputs guarantees the first text block is schema-valid JSON.
    # (A thinking block may precede it, hence the filter on block type.)
    text = next((b.text for b in response.content if b.type == "text"), None)
    if not text:
        raise VisionExtractionError("Vision LLM returned no text content")

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise VisionExtractionError(f"Vision LLM returned invalid JSON: {exc}") from exc
