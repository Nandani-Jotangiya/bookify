from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import SECRET_KEY, STATIC_DIR
from app.db_init import initialize_database
from app.routes.admin.books import router as books_router
from app.routes.admin.category import router as category_router
from app.routes.admin.dashboard import router as dashboard_router
from app.routes.admin.history import router as history_router
from app.routes.admin.issued_book import router as issued_book_router
from app.routes.admin.requests import router as requests_router
from app.routes.auth import router as auth_router
from app.routes.payment import router as payment_router
from app.routes.user import router as user_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def home():
    return RedirectResponse(url="/login", status_code=303)


app.include_router(payment_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(dashboard_router)
app.include_router(category_router)
app.include_router(books_router)
app.include_router(requests_router)
app.include_router(issued_book_router)
app.include_router(history_router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Session middleware stores CSRF tokens; JWT auth uses the access_token cookie.
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
