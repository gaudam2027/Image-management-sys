from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, select, func
from sqlalchemy.orm import relationship,column_property
from config.db import Base
from datetime import datetime
from models.image_likes_model import ImageLike
import enum

class VisibilityEnum(enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    file_path = Column(String(255))
    file_size = Column(Integer)

    tags = relationship("ImageTag", back_populates="image", cascade="all, delete")
    likes = relationship("ImageLike", back_populates="image", cascade="all, delete")
    
    like_count = column_property(
        select(func.count(ImageLike.id))
        .where(ImageLike.image_id == id)
        .correlate_except(ImageLike)
        .scalar_subquery()
    )
    
    is_favorite = Column(Boolean, default=False)
    
    is_deleted = Column(Boolean, default=False)
    
    visibility = Column(Enum(VisibilityEnum), default=VisibilityEnum.PRIVATE)

    created_at = Column(DateTime, default=datetime.utcnow)