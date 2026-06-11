from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles 
import os

from app.database import engine
from app.models import Base
from app.routes.auth import router as auth_router

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)

app = FastAPI() 

@app.get("/")
def home():
    return {"message": "Working!"}

app.include_router(auth_router)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static"
)
