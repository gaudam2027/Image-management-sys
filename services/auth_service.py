from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.user_model import User
from utils.security import hash_password, verify_password, create_access_token
from utils.logger import get_logger

logger = get_logger(__name__)


def signup_user(db: Session, data):
    logger.info(f"Signup attempt for email: {data.email}")

    user = db.query(User).filter(User.email == data.email).first()
    if user:
        logger.warning(f"Signup failed - Email already exists: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    try:
        new_user = User(
            name=data.name,
            email=data.email,
            password=hash_password(data.password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"User created successfully: {new_user.id}")

        return {"message": "User created"}

    except Exception:
        logger.exception("Error during user signup")
        raise


def login_user(db: Session, data):
    logger.info(f"Login attempt for email: {data.email}")

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        logger.warning(f"Login failed - Invalid email: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid email"
        )

    if not verify_password(data.password, user.password):
        logger.warning(f"Login failed - Wrong password for: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    if user.is_blocked:
        logger.warning(f"Blocked user tried login: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is blocked"
        )

    try:
        token = create_access_token({"user_id": user.id})

        logger.info(f"User logged in successfully: {user.id}")

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except Exception:
        logger.exception("Error during login")
        raise