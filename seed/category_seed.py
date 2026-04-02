from sqlalchemy.orm import Session
from config.db import SessionLocal
from models.category_model import Category


DEFAULT_CATEGORIES = [
    "People",
    "Nature",
    "Things"
]

def seed_categories():
    db: Session = SessionLocal()
    try:
        for name in DEFAULT_CATEGORIES:
            exist = db.query(Category).filter(Category.name == name).first()
            if not exist:
                db.add(Category(name=name))
        db.commit()
    finally:
        db.close()        