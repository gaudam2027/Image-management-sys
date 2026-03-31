from sqlalchemy import Column, Integer, String, Boolean, DateTime
from config.db import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))

    is_admin = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)

    storage_limit = Column(Integer, default=50)  # MB

    created_at = Column(DateTime, default=datetime.utcnow)