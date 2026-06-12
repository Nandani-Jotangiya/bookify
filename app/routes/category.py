from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Category import Category
router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/categories")
def category_page(
    request: Request,
    db: Session = Depends(get_db)
):
    categories = db.query(Category).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/categories.html",
        context={
            "categories": categories
        }
    ) 

@router.get("/categories/add")
def add_category_page(
    request:Request,
):
    
    return templates.TemplateResponse (
        request=request,
        name="admin/add_categories.html"
    )
    

@router.post("/categories/add")
def save_category(
    name:str = Form(...),
    db:Session = Depends(get_db)
):
    
    name = name.strip()

    if not name:
        return {
            "message": "Category name is required"
        }
    
    existing_category = (
        db.query(Category).filter(Category.name == name).first()
    )

    if existing_category :
        return {
            "message": "Category already exists"
        }
  
    category = Category(name=name)

    db.add(category)
    db.commit()

    return RedirectResponse (
        url="/categories",
        status_code=303
    )