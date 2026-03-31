from models.user_model import User

def get_all_users(db):
    users = db.query(User).filter(User.is_admin == False).all()
    return users

def block_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    user.is_blocked = True
    db.commit()
    return {"message": "User blocked successfully"}

def unblock_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    user.is_blocked = False
    db.commit()
    return {"message": "User unblocked successfully"}