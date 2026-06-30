from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from app.database import engine
from app.models import Category, Book
from app.models.User import Base
from app.routes.auth import router as auth_router
from app.routes.category import router as category_router
from app.routes.books import router as books_router

from app.routes.user import router as user_router
from app.routes.requests import router as request_route
from app.routes.admin.issued_book import router as issuedBook_router


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)

app = FastAPI()

load_dotenv()


@app.get("/")
def home():
    return {"message": "Working!"}


app.include_router(auth_router)
app.include_router(category_router)
app.include_router(books_router)
app.include_router(user_router)
app.include_router(request_route)
app.include_router(issuedBook_router)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static",
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
