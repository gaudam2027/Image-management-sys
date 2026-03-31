from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies.auth import get_current_user,get_admin_user
from config.db import get_db
from services.admin_service import get_all_users,block_user,unblock_user
from schemas.user_schema import AdminResponse,UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/me", response_model=AdminResponse)
def get_admin_profile(
    admin = Depends(get_admin_user),db: Session = Depends(get_db)):
    return admin

@router.get("/users", response_model=list[UserResponse])
def get_users(
    admin = Depends(get_admin_user),db: Session = Depends(get_db)):
    return get_all_users(db)

@router.put("/block/{user_id}")
def block_user_route(user_id: int,admin = Depends(get_admin_user),db: Session = Depends(get_db)):
    return block_user(db, user_id)

@router.put("/unblock/{user_id}")
def unblock_user_route(user_id: int,admin = Depends(get_admin_user),db: Session = Depends(get_db)):
    return unblock_user(db, user_id)

