from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from config.db import Base
from datetime import datetime

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    file_path = Column(String(255))
    file_size = Column(Integer)

    tags = Column(JSON)
    
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)