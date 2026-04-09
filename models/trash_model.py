from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime

class Trash(Base):
    __tablename__ = "trash"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)

    moved_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("Image")