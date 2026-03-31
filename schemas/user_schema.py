from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

class AdminResponse(BaseModel):
    id: int
    name: str
    email: str
    is_admin: bool  

    class Config:
        from_attributes = True