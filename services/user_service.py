from models.user_model import User
from fastapi import HTTPException
from utils.logger import get_logger

logger = get_logger(__name__)
def get_user_profile(current_user, db):
    user = db.query(User).filter(
        User.id == current_user.id
    ).first()

    if not user:
        logger.info(f"Fetch profile | user_id={current_user.id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"Profile fetched successfully | user_id={user.id}")
    return user