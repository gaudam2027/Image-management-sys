import os
import shutil
import uuid
from fastapi import HTTPException
from models.image_model import Image
from models.category_model import Category

def get_user_images(current_user, db, category_id=None, tags=None):
    query = db.query(Image).filter(
        Image.user_id == current_user.id,
        Image.is_deleted == False
    )
    
    if category_id:
        query = query.filter(Image.category_id == category_id)
    images = query.all()
    if tags:
        tags_list = [tag.strip().lower() for tag in tags.split(",")]
        print(tags_list)
        query = query.filter(Image.tags.contains(tags_list))
        images = [
            img for img in images
            if img.tags and all(tag in img.tags for tag in tags_list)
        ]

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
        
    if tags:
        tags = [tag.strip().lower() for tag in tags.split(",")]

    new_image = Image(
        user_id=current_user.id,
        category_id=category_id,
        file_path=file_path,
        file_size=0,
        tags=tags
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)

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
        image.tags = [tag.strip().lower() for tag in tags.split(",")]
    
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
    
    