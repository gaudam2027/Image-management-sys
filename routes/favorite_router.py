from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from config.db import get_db
from dependencies.auth import get_current_user
from schemas.image_schema import ImageResponse
from services.favorite_service import get_favorite_images, add_to_fav, remove_from_fav

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("/", response_model=List[ImageResponse])
def get_favorites(current_user = Depends(get_current_user),db: Session = Depends(get_db)):
    return get_favorite_images(current_user, db)


@router.post("/{id}", response_model=ImageResponse)
def add_favorite(
    id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return add_to_fav(id, current_user, db)


@router.delete("/{id}", response_model=ImageResponse)
def remove_favorite(
    id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return remove_from_fav(id, current_user, db)