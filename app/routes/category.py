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
         "request": request,
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
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db)
):

    name = name.strip()

    if not name:
        return templates.TemplateResponse(
            request=request,
            name="admin/add_categories.html",
            context={
                "error": "Category name is required"
            }
        )

    existing_category = (
        db.query(Category)
        .filter(Category.name == name)
        .first()
    )

    if existing_category:
        return templates.TemplateResponse(
            request=request,
            name="admin/add_categories.html",
            context={
                "error": "Category already exists",
                "name": name
            }
        )

    category = Category(name=name)

    db.add(category)
    db.commit()

    return RedirectResponse(
        url="/categories",
        status_code=303
    )

#EDIT CATEGORY PAGE

@router.get("/categories/edit/{id}")
def edit_category_page(
    id:int,
    request:Request,
    db:Session = Depends(get_db)
    ):

    category = (db.query(Category).filter(Category.id == id).first())

    if not category : 
        return RedirectResponse(
            url="/categories",
            status_code=303
        )
    
    return templates.TemplateResponse (
        request=request,
        name="admin/edit_category.html",
        context= {
            "request":request,
            "category":category
        }
    )

#UPDATE CATEGORY
@router.post("/categories/edit/{id}")
def update_category(
    id:int,
    name: str = Form(...),
    db:Session = Depends(get_db)
):
    category = (db.query(Category).filter(Category.id == id).first())

    if category:
        category.name = name 
        db.commit()

    return RedirectResponse(
        url="/categories",
        status_code=303
    )

#DELETE CATEGORY
@router.get("/categories/delete/{id}")
def delete_category(
    id:int,
    db:Session = Depends(get_db)
):
    
    category = db.query(Category).filter(Category.id == id).first()

    if category:
        db.delete(category)
        db.commit()

    return RedirectResponse(
        url="/categories",
        status_code=303
    )
