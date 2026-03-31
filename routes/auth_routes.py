from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.db import get_db
from schemas.auth_schema import SignupSchema, LoginSchema
from services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup")
def signup(data: SignupSchema, db: Session = Depends(get_db)):
    return auth_service.signup_user(db, data)


@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    return auth_service.login_user(db, data)