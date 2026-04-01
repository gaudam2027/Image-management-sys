from models.user_model import User
from utils.logger import get_logger
from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import HTTPException


logger = get_logger(__name__)

def get_all_users(db, search=None, page=1):
    PER_PAGE = 2
    query = db.query(User).filter(User.is_admin == False)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    offset = (page - 1) * PER_PAGE
    users = query.order_by(User.id).offset(offset).limit(PER_PAGE).all()
    return users

def block_user(db: Session, user_id: int):
    logger.info(f"Block user attempt | user_id={user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"User not found | user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_admin:
        raise HTTPException(403, "Cannot block admin")
    if user.is_blocked:
        logger.warning(f"User already blocked | user_id={user_id}")
        raise HTTPException(status_code=400, detail="User is blocked")
    try:
        user.is_blocked = True
        db.commit()
        logger.info(f"User blocked successfully | user_id={user_id}")
        return {"message": "User blocked successfully"}
    except Exception:
        logger.exception(f"Error blocking user | user_id={user_id}")
        raise

def unblock_user(db: Session, user_id: int):
    logger.info(f"Unblock user attempt | user_id={user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"User not found | user_id={user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_blocked:
        logger.warning(f"User already active | user_id={user_id}")
        raise HTTPException(status_code=400, detail="User is not blocked")
    try:
        user.is_blocked = False
        db.commit()
        logger.info(f"User unblocked successfully | user_id={user_id}")
        return {"message": "User unblocked successfully"}
    except Exception:
        logger.exception(f"Error unblocking user | user_id={user_id}")
        raise