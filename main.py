from fastapi import FastAPI, Request
from config.db import Base, engine
from routes import auth_routes,user_routes,image_routes,admin_routes
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from utils.logger import get_logger

from models.user_model import User
from models.image_model import Image
from models.category_model import Category

app = FastAPI()
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(image_routes.router)
app.include_router(admin_routes.router)

logger = get_logger("global")

Base.metadata.create_all(bind=engine)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        f"HTTPException | {request.method} {request.url} | "
        f"Status: {exc.status_code} | Detail: {exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
    
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        f"Unhandled Error | Path: {request.url}"
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )