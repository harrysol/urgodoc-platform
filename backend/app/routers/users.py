"""User endpoints: save / fetch custom avatar body dimensions."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import UserProfile
from ..schemas import UserDimensionsRequest, UserProfileResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.put(
    "/{user_id}/dimensions",
    response_model=UserProfileResponse,
    summary="Create or update a user's body dimensions",
)
def upsert_dimensions(
    user_id: str,
    payload: UserDimensionsRequest,
    db: Session = Depends(get_db),
) -> UserProfile:
    """Upsert the measurements captured via the on-device MediaPipe calibration."""
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    if profile is None:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    # Only overwrite fields that were actually provided in the request.
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.get(
    "/{user_id}/dimensions",
    response_model=UserProfileResponse,
    summary="Fetch a user's saved body dimensions",
)
def get_dimensions(user_id: str, db: Session = Depends(get_db)) -> UserProfile:
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    if profile is None:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile
