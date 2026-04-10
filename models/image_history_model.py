from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from config.db import Base

class ImageHistory(Base):
    __tablename__ = "image_history"

    id = Column(Integer, primary_key=True, index=True)

    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)

    old_title = Column(String(255))
    new_title = Column(String(255))

    updated_at = Column(DateTime, default=datetime.utcnow)