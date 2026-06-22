"""Product endpoints: submit a link, poll task status, list jobs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Product
from ..schemas import (
    ProductDetailResponse,
    ProductSubmitRequest,
    ProductTaskResponse,
)
from ..services.affiliate import to_affiliate_url
from ..tasks import process_product_task

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "/submit",
    response_model=ProductTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a retail link for processing",
)
def submit_product(
    payload: ProductSubmitRequest,
    db: Session = Depends(get_db),
) -> Product:
    """Create a job row, generate the affiliate link, and enqueue the AI pipeline."""
    source_url = str(payload.url)
    product = Product(
        source_url=source_url,
        affiliate_url=to_affiliate_url(source_url),
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Hand off to the Celery worker; the client polls GET /products/{id}.
    process_product_task.delay(product.id)
    return product


@router.get(
    "/{product_id}",
    response_model=ProductDetailResponse,
    summary="Poll the status / result of a job",
)
def get_product(product_id: str, db: Session = Depends(get_db)) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get(
    "",
    response_model=list[ProductDetailResponse],
    summary="List recent jobs",
)
def list_products(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[Product]:
    stmt = (
        select(Product)
        .order_by(Product.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt).all())
