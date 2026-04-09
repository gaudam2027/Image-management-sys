from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from config.db import get_db
from dependencies.auth import get_current_user
from typing import List, Optional
from services.trash_service import get_user_trash,move_to_trash,restore_images,permanent_delete


router = APIRouter(prefix="/trash", tags=["Trash"])

@router.get("/list")
def fetch_user_trash(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_trash(db, current_user.id)

@router.post("/move")
def move_images_to_trash(
    image_ids: List[int] = Query(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return move_to_trash(db, current_user.id, image_ids)

@router.post("/restore")
def restore_images_from_trash(
    image_ids: List[int] = Query(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return restore_images(db, current_user.id, image_ids)

@router.delete("/permanent")
def permanent_delete_images(
    image_ids: List[int] = Query(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return permanent_delete(db, current_user.id, image_ids)