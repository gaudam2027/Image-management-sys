import os
import shutil
import uuid
from fastapi import HTTPException
from datetime import datetime
from models.image_model import Image, VisibilityEnum
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from models.image_tags_model import ImageTag
from models.category_model import Category
from models import Trash,ImageLike
from utils.logger import get_logger

logger = get_logger(__name__)

UPLOAD_DIR = "uploads"


def get_user_images(current_user, db, page=1, category_id=None, tags=None, start_date: str = None, end_date: str = None):
    PER_PAGE = 5
    
    logger.info(f"Fetch images | user_id={current_user.id} | page={page}")

    trashed_image_ids = db.query(Trash.image_id).filter(Trash.user_id == current_user.id).subquery()
    
    query = db.query(Image).filter(
        Image.user_id == current_user.id,
        Image.is_deleted == False,
        ~Image.id.in_(trashed_image_ids)
    )
    
    start_dt = None
    end_dt = None
    
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end_dt = datetime.combine(datetime.utcnow().date(), datetime.max.time())
    elif end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
    if start_dt and end_dt:
        query = query.filter(Image.created_at >= start_dt, Image.created_at <= end_dt)
    elif start_dt:
        query = query.filter(Image.created_at >= start_dt)
    elif end_dt:
        query = query.filter(Image.created_at <= end_dt)
        
    if category_id:
        logger.info(f"Filter by category | category_id={category_id}")
        query = query.filter(Image.category_id == category_id)

    if tags:
        tags_list = [tag.strip().lower() for tag in tags.split(",")]
        logger.info(f"Filter by tags | tags={tags_list}")

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

    logger.info(f"Images fetched | count={len(images)}")

    return images

def save_image(file, current_user, category_id, tags, db):
    logger.info(f"Upload image attempt | user_id={current_user.id}")

    if file.content_type not in ["image/jpeg", "image/png"]:
        logger.warning(f"Invalid file type | user_id={current_user.id}")
        raise HTTPException(status_code=400, detail="Invalid file type")

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        logger.warning(f"Category not found | category_id={category_id}")
        raise HTTPException(status_code=404, detail="Category not found")

    try:
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

        logger.info(f"Image saved | image_id={new_image.id}")

        if tags:
            tags_list = [tag.strip().lower() for tag in tags.split(",")]

            tag_objects = [
                ImageTag(image_id=new_image.id, tag=tag)
                for tag in tags_list
            ]

            db.add_all(tag_objects)
            db.commit()
            logger.info(f"Tags added | image_id={new_image.id} | tags={tags_list}")

        return new_image

    except Exception:
        logger.exception(f"Error saving image | user_id={current_user.id}")
        raise


def update_image(image_id, file, current_user, db, category_id=None, tags=None):
    logger.info(f"Update image attempt | image_id={image_id} | user_id={current_user.id}")
    trashed_image_ids = db.query(Trash.image_id).filter(Trash.user_id == current_user.id).subquery()
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.is_deleted == False,
        ~Image.id.in_(trashed_image_ids)
        ).first()

    if not image:
        logger.warning(f"Image not found | image_id={image_id}")
        raise HTTPException(status_code=404, detail="Image not found")

    if image.user_id != current_user.id:
        logger.warning(f"Unauthorized update attempt | image_id={image_id}")
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
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

            logger.info(f"Tags updated | image_id={image.id} | tags={tags_list}")

        if file:
            if image.file_path and os.path.exists(image.file_path):
                os.remove(image.file_path)

            file_ext = file.filename.split(".")[-1]
            unique_name = f"{uuid.uuid4()}.{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_name)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            image.file_path = file_path
            image.file_size = 0

            logger.info(f"Image file updated | image_id={image.id}")

        db.commit()
        db.refresh(image)

        logger.info(f"Image updated successfully | image_id={image.id}")

        return image

    except Exception:
        logger.exception(f"Error updating image | image_id={image_id}")
        raise

    
def toggle_image_visibility(current_user,db, image_id: int):
    logger.info(f"Toggle visibility | image_id={image_id} | user_id={current_user.id}")
    
    trashed_image_ids = db.query(Trash.image_id).filter(Trash.user_id == current_user.id).subquery()
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id,
        Image.is_deleted == False,
        ~Image.id.in_(trashed_image_ids)
    ).first()
    
    if not image:
        logger.warning(f"Image not found | image_id={image_id}")
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        if image.visibility == VisibilityEnum.PRIVATE:
            image.visibility = VisibilityEnum.PUBLIC
        else:
            image.visibility = VisibilityEnum.PRIVATE

        db.commit()
        db.refresh(image)

        logger.info(f"Visibility toggled | image_id={image.id} | new_visibility={image.visibility}")

        return image
    
    except Exception:
        logger.exception(f"Error toggling visibility | image_id={image_id}")
        raise
    
def get_public_images(current_user,db, page=1, category_id=None, tags=None):
    PER_PAGE = 5
    logger.info(f"Fetch public images | page={page}")

    trashed_image_ids = db.query(Trash.image_id).subquery()
    query = db.query(Image).filter(
        Image.visibility == VisibilityEnum.PUBLIC,
        Image.is_deleted == False,
        ~Image.id.in_(trashed_image_ids)
    )
    
    if category_id:
        query = query.filter(Image.category_id == category_id)
        
    if tags:
        tags_list = [tag.strip().lower() for tag in tags.split(",")]
        logger.info(f"Filter by tags | tags={tags_list}")

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

    logger.info(f"Public images fetched | count={len(images)}")

    return images
        
    
def toggle_like_image(current_user, db, image_id: int):
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.is_deleted == False,
        Image.visibility == VisibilityEnum.PUBLIC
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Public image not found")
    
    existing_like = db.query(ImageLike).filter(
        ImageLike.image_id == image.id,
        ImageLike.user_id == current_user.id
    ).first()
        
    if existing_like:
        db.delete(existing_like)
        db.commit()
        return {"liked": False, "image_id": image.id}
    else:
        new_like = ImageLike(image_id=image.id, user_id=current_user.id)
        db.add(new_like)
        db.commit()
        return {"liked": True, "image_id": image.id}
    
    