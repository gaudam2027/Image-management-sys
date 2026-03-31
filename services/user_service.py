from models.user_model import User
from fastapi import HTTPException

def get_user_profile(current_user, db):
    user = db.query(User).filter(
        User.id == current_user.id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user