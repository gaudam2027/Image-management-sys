from fastapi import HTTPException
from models.image_model import Image
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from utils.logger import get_logger

logger = get_logger(__name__)

UPLOAD_DIR = "uploads"

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
        return image

    image.is_favorite = False

    db.commit()
    db.refresh(image)

    logger.info(f"Image removed from favorite | image_id={image.id}")

    return image