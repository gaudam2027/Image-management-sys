from models.category_model import Category
from fastapi import HTTPException

def create_category(data, db):

    check_existing = db.query(Category).filter(Category.name == data.name).first()

    if check_existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = Category(name=data.name)

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category