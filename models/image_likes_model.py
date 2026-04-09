from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime


class ImageLike(Base):
    __tablename__ = "image_likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_id = Column(Integer, ForeignKey("images.id"))

    image = relationship("Image", back_populates="likes")
    created_at = Column(DateTime, default=datetime.utcnow)