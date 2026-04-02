import os
import shutil
import uuid
from fastapi import HTTPException
from models.image_model import Image
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from models.image_tags_model import ImageTag
from models.category_model import Category
from utils.logger import get_logger

logger = get_logger(__name__)

UPLOAD_DIR = "uploads"


def get_user_images(current_user, db, page=1, category_id=None, tags=None):
    PER_PAGE = 2
    
    logger.info(f"Fetch images | user_id={current_user.id} | page={page}")

    query = db.query(Image).filter(
        Image.user_id == current_user.id,
        Image.is_deleted == False
    )

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

    image = db.query(Image).filter(Image.id == image_id).first()

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


def delete_image(image_id, current_user, db):
    logger.info(f"Delete image attempt | image_id={image_id} | user_id={current_user.id}")

    image = db.query(Image).filter(Image.id == image_id).first()

    if not image:
        logger.warning(f"Image not found | image_id={image_id}")
        raise HTTPException(status_code=404, detail="Image not found")

    if image.user_id != current_user.id:
        logger.warning(f"Unauthorized delete attempt | image_id={image_id}")
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        image.is_deleted = True

        db.commit()
        db.refresh(image)
        logger.info(f"Image soft deleted | image_id={image.id}")

        return image

    except Exception:
        logger.exception(f"Error deleting image | image_id={image_id}")
        raise
    
# -------------------------------------favorites----------------------

def get_favorite_images(current_user,db):
    favorities = db.query(Image).filter(
        Image.user_id == current_user.id,
        Image.is_favorite == True,
        Image.is_deleted == False
    ).options(joinedload(Image.tags)).all()
    
    return favorities

def add_to_fav(image_id, current_user, db):
    logger.info(f"Add to favorite | image_id={image_id} | user_id={current_user.id}")

    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id,
        Image.is_deleted == False
    ).first()

    if not image:
        logger.warning(f"Image not found | image_id={image_id}")
        raise HTTPException(status_code=404, detail="Image not found")

    if image.is_favorite:
        logger.info(f"Image already favorite | image_id={image_id}")
        return image 
    
    image.is_favorite = True
    db.commit()
    db.refresh(image)

    logger.info(f"Image added to favorite | image_id={image.id} | is_favorite={image.is_favorite}")

    return image
    
def remove_from_fav(image_id, current_user, db):
    logger.info(f"Remove from favorite | image_id={image_id} | user_id={current_user.id}")

    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id,
        Image.is_deleted == False
    ).first()

    if not image:
        logger.warning(f"Image not found | image_id={image_id}")
        raise HTTPException(status_code=404, detail="Image not found")

    if not image.is_favorite:
        logger.info(f"Image already not favorite | image_id={image_id}")
        return image  # already not favorite

    image.is_favorite = False

    db.commit()
    db.refresh(image)

    logger.info(f"Image removed from favorite | image_id={image.id}")

    return image