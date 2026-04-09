from sqlalchemy.orm import Session,joinedload
from fastapi import HTTPException
from typing import List
from datetime import datetime, timedelta

from models import Image, Trash
from utils.logger import get_logger

logger = get_logger(__name__)

def get_user_trash(db: Session, user_id: int):
    try:
        logger.info(f"listing trash {user_id}")
        trash_items = db.query(Trash).options(joinedload(Trash.image)).filter(
            Trash.user_id == user_id
        ).all()
        logger.info(f"Fetched {len(trash_items)} trash items for user_id={user_id}")
        return trash_items
    except Exception:
        logger.exception(f"Error fetching trash for user_id={user_id}")
        raise
    
def move_to_trash(db,user_id,image_ids:List[int]):
    try:
        images = db.query(Image).filter(
            Image.id.in_(image_ids),
            Image.user_id == user_id,
            Image.is_deleted == False
        ).all()
        
        if not images:
            logger.warning(f"No images found to move to trash for user {user_id}")
            raise HTTPException(status_code=404, detail="Images not found")
        
        existing_trash = db.query(Trash.image_id).filter(Trash.image_id.in_(image_ids),Trash.user_id == user_id).all()
        
        existing_ids = {t.image_id for t in existing_trash}
        
        for image in images:
            if image.id not in existing_ids:
                trash = Trash(
                    user_id=user_id,
                    image_id=image.id,
                    moved_at=datetime.utcnow()
                )
                db.add(trash)
                logger.info(f"Image {image.id} moved to trash for user {user_id}")
            
        db.commit()
        logger.info(f"Images successfully moved to trash for user {user_id}")
        
        return {"message": "Images moved to trash"}
    
    except Exception:
        logger.exception(f"Error moving images to trash for user {user_id}")
        raise


def restore_images(db, user_id, image_ids: List[int]):
    try:
        trash_items = db.query(Trash).filter(
            Trash.image_id.in_(image_ids),
            Trash.user_id == user_id
        ).all()

        if not trash_items:
            logger.warning(f"No trash items found to restore for user {user_id}")
            raise HTTPException(status_code=404, detail="Trash items not found")

        
        for item in trash_items:
            db.delete(item)
            logger.info(f"Restored image {item.image_id} from trash for user {user_id}")

        db.commit()
        logger.info(f"Successfully restored {len(trash_items)} images for user {user_id}")
        
        return {"message": "Images restored successfully"}

    except Exception:
            logger.exception(f"Error restoring images from trash for user {user_id}")
            raise


def permanent_delete(db: Session, user_id: int, image_ids: List[int]):
    try:
        trash_items = db.query(Trash).filter(
            Trash.image_id.in_(image_ids),
            Trash.user_id == user_id
        ).all()

        if not trash_items:
            logger.warning(f"No trash items found for permanent deletion for user {user_id}")
            raise HTTPException(status_code=404, detail="Items not in trash")
        
        image_ids_from_trash = [item.image_id for item in trash_items]
        
        images = db.query(Image).filter(
            Image.id.in_(image_ids_from_trash),
            Image.user_id == user_id
        ).all()

        for image in images:
            image.is_deleted = True
            logger.info(f"Marked image {image.id} as deleted for user {user_id}")
            
        for item in trash_items:
            db.delete(item)
            logger.info(f"Removed image {item.image_id} from trash for user {user_id}")

        db.commit()
        logger.info(f"Successfully permanently deleted {len(images)} images for user {user_id}")
        return {"message": "Images permanently deleted"}
    
    except Exception:
        logger.exception(f"Error permanently deleting images for user {user_id}")
        raise
    
def auto_permanent_delete(db: Session):
    try:
        cutoff_time = datetime.utcnow() - timedelta(minutes=2)
        logger.info(f"Starting auto permanent delete job | cutoff_time={cutoff_time}")
        
        old_trash_items = db.query(Trash).filter(
            Trash.moved_at <= cutoff_time
        ).all()
        
        if not old_trash_items:
            logger.info("No images eligible for auto deletion")
            return {"message": "No images to delete"}
        
        image_ids = [item.image_id for item in old_trash_items]
        
        images = db.query(Image).filter(
            Image.id.in_(image_ids)
        ).all()
        
        for image in images:
            image.is_deleted = True
            logger.info(f"Auto deleted image_id={image.id}")
            
        for item in old_trash_items:
            db.delete(item)

        db.commit()
        
        logger.info(f"Auto permanent delete completed | count={len(images)}")

        return {"message": f"{len(images)} images auto deleted"}
    
    except Exception:
        logger.exception(f"Error while auto clearing old trash items")
        raise
        