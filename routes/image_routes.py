from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session

from config.db import get_db
from dependencies.auth import get_current_user
from schemas.image_schema import ImageResponse
from typing import List, Optional
from services.image_service import get_user_images,save_image,update_image,delete_image

router = APIRouter(prefix="/img", tags=["Images"])

@router.get("/images", response_model=List[ImageResponse])
def get_images(
    page: int = Query(1),
    category_id: Optional[int] = None,
    tags: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    images = get_user_images(current_user, db, page, category_id, tags)
    return images


@router.post("/upload", response_model=ImageResponse)
def upload_image(
    file: UploadFile = File(...),
    category_id: int = Form(...),
    tags: str = Form(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_image = save_image(file, current_user, category_id, tags, db)
    return new_image

@router.put("/update/{id}",response_model=ImageResponse)
def update_img(
    id: int,
    file: UploadFile = File(None),
    category_id: int = Form(None),
    tags: Optional[str] = Form(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated_image = update_image(id, file, current_user, db, category_id, tags)
    return updated_image

@router.delete("/delete/{id}",response_model=ImageResponse)
def delete_img(id: int,current_user = Depends(get_current_user),db: Session = Depends(get_db)):
    image = delete_image(id, current_user, db)
    return image