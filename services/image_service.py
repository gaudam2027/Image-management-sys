import os
import shutil
import uuid
from fastapi import HTTPException
from models.image_model import Image
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from models.image_tags_model import ImageTag
from models.category_model import Category

def get_user_images(current_user, db, page=1, category_id=None, tags=None):
    PER_PAGE = 2
    
    page = page or 1
    
    query = db.query(Image).filter(
        Image.user_id == current_user.id,
        Image.is_deleted == False
    )
    
    if category_id:
        query = query.filter(Image.category_id == category_id)
    if tags:
        tags_list = [tag.strip().lower() for tag in tags.split(",")]
        query = query.join(ImageTag).filter(ImageTag.tag.in_(tags_list))

        query = query.group_by(Image.id).having(
            func.count(ImageTag.tag) == len(tags_list)
        )
        
    offset = (page - 1) * PER_PAGE

    images = (
        query.options(joinedload(Image.tags))
        .order_by(Image.id.desc())
        .offset(offset)
        .limit(PER_PAGE)
        .all()
    )

    return images

UPLOAD_DIR = "uploads"

def save_image(file, current_user, category_id, tags, db):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_ext = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_image = Image(
        user_id=current_user.id,
        category_id=category_id,
        file_path=file_path,
        file_size=0,
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    
    if tags:
        tags_list = [tag.strip().lower() for tag in tags.split(",")]

        tag_objects = [
            ImageTag(image_id=new_image.id, tag=tag)
            for tag in tags_list
        ]
        
        db.add_all(tag_objects)
        db.commit()

    return new_image

def update_image(image_id, file, current_user, db, category_id=None, tags=None):
    image = db.query(Image).filter(Image.id == image_id).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    if image.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if category_id is not None:
        image.category_id = category_id
    
    if tags is not None:
        db.query(ImageTag).filter(ImageTag.image_id == image.id).delete()
        
        tags_list = [tag.strip().lower() for tag in tags.split(",")]
        
        new_tags = [
            ImageTag(image_id=image.id, tag=tag)
            for tag in tags_list
        ]

        db.add_all(new_tags)
    
    if file:
        if image.file_path and os.path.exists(image.file_path):
            os.remove(image.file_path)
            
        file_ext = file.filename.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join("uploads", unique_name)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        image.file_path = file_path
        image.file_size = 0
    db.commit()
    db.refresh(image)
    
    return image
    
    
def delete_image(image_id, current_user, db):
    image = db.query(Image).filter(Image.id == image_id).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    if image.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    image.is_deleted = True
    
    db.commit()
    db.refresh(image)
    
    return image
    
    