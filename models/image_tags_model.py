from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base

class ImageTag(Base):
    __tablename__ = "image_tags"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"))
    tag = Column(String(100), index=True)

    image = relationship("Image", back_populates="tags")