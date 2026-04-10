from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from config.db import get_db
from dependencies.auth import get_current_user
from schemas.image_schema import ImageResponse,ImageHistoryResponse
from typing import List, Optional
from services.image_service import get_user_images,save_image,update_image,toggle_image_visibility,get_public_images,toggle_like_image,get_image_history

router = APIRouter(prefix="/img", tags=["Images"])

@router.get("/", response_model=List[ImageResponse])
def get_images(
    page: int = Query(1),
    category_id: Optional[int] = None,
    tags: Optional[str] = None,
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    images = get_user_images(current_user, db, page, category_id, tags,start_date,end_date)
    return images


@router.post("/upload", response_model=ImageResponse)
def upload_image(
    file: UploadFile = File(...),
    category_id: int = Form(...),
    title: str = Form(...),
    tags: str = Form(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_image = save_image(file, current_user, category_id, title, tags, db)
    return new_image

@router.put("/update/{id}",response_model=ImageResponse)
def update_img(
    id: int,
    file: UploadFile = File(None),
    category_id: int = Form(None),
    tags: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated_image = update_image(id, file, current_user, db, category_id, tags, title)
    return updated_image


@router.patch("/visibility/{image_id}", response_model=ImageResponse)
def toggle_visibility(
    image_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    image = toggle_image_visibility(current_user, db, image_id)
    return image


@router.get("/public", response_model=List[ImageResponse])
def public_feed(
    page: int = Query(1),
    category_id: Optional[int] = None,
    current_user = Depends(get_current_user),
    tags: Optional[str] = None,
    db: Session = Depends(get_db)
):
    images = get_public_images(current_user, db, page, category_id, tags)
    return images


@router.post("/like/{image_id}")
def like_image(
    image_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return toggle_like_image(current_user, db, image_id)

@router.get("/{image_id}/history", response_model=List[ImageHistoryResponse])
def image_history(
    image_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_image_history(image_id, current_user, db)