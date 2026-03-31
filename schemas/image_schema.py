from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime

class ImageResponse(BaseModel):
    id: int
    user_id: int
    category_id: Optional[int]
    file_path: str
    file_size: int
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True 
        