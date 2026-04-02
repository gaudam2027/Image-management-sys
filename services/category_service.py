from models.category_model import Category
from fastapi import HTTPException
from utils.logger import get_logger
logger = get_logger(__name__)


def get_category(db):
    logger.info(f"Fetching all category")
    try:
        Categories = db.query(Category).all()
        return Categories
    except Exception:
        logger.exception("Error fetching categories")
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
    

def create_category(data, db):
    logger.info(f"Create category attempt | name={data.name}")

    existing = db.query(Category).filter(Category.name == data.name).first()

    if existing:
        logger.warning(f"Category already exists | name={data.name}")
        raise HTTPException(status_code=400, detail="Category already exists")
    try:
        new_category = Category(name=data.name)

        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        logger.info(f"Category created | id={new_category.id} | name={data.name}")

        return new_category

    except Exception:
        logger.exception(f"Error creating category | name={data.name}")
        raise