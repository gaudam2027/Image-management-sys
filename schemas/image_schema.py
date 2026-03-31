from pydantic import BaseModel, field_validator
from typing import Optional,List
from datetime import datetime

class ImageResponse(BaseModel):
    id: int
    user_id: int
    category_id: Optional[int]
    file_path: str
    file_size: int
    tags: List[str]
    created_at: datetime

    class Config:
        from_attributes = True 
        
    @field_validator("tags", mode="before")
    @classmethod
    def convert_tags(cls, value):
        if isinstance(value, list):
            return [t.tag if hasattr(t, "tag") else t for t in value]
        return value
        