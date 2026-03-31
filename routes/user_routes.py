from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies.auth import get_current_user
from config.db import get_db
from services.user_service import get_user_profile
from schemas.user_schema import UserResponse
from schemas.category_schema import CategoryCreate,CategoryResponse
from services.category_service import create_category


router = APIRouter(prefix="/user", tags=["User"])

@router.get("/profile",response_model=UserResponse)
def home(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user =get_user_profile(current_user, db)
    return user

@router.post("/category",response_model=CategoryResponse)
def add_cat(
    data: CategoryCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = create_category(data, db)
    return category


