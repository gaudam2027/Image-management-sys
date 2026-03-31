from fastapi import FastAPI
from config.db import Base, engine
from routes import auth_routes,user_routes,image_routes,admin_routes

from models.user_model import User
from models.image_model import Image
from models.category_model import Category

app = FastAPI()
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(image_routes.router)
app.include_router(admin_routes.router)

Base.metadata.create_all(bind=engine)