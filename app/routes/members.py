from fastapi import APIRouter, Request, Depends,Form
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.database import get_db
from app.models.Member import Member

router = APIRouter()

templates = Jinja2Templates(directory="templates")

#MEMBER PAGE
@router.get("/members")
def get_members_page(
    request: Request,
    db: Session = Depends(get_db)
):
    members = db.query(Member).all()

    return templates.TemplateResponse(
        "admin/members.html",
        {
            "request": request,
            "members": members
        }
    )


#ADD MEMBER PAGE
@router.get("/members/add")
def add_member_page(request:Request):
    return templates.TemplateResponse (
        "admin/add_member.html",
        {
            "request":request
        }
    )
    
#SAVE MEMBER

@router.post("/member/add")
def save_member(
    
    db:Session = Depends(get_db),
    name:str = Form(...),
    email:str = Form(...),
    address:str = Form(None),
    phone:str = Form(...),
    status:str = Form("Active")
):
    name = name.strip()
    email = email.strip()
    phone = phone.strip()

    if not name :
        return {"message":"Name is required"}
    
    if not email :
        return {"message":"Name is required"}
    
    if not phone :
        return {"message":"Name is required"}
    
    existing_member = db.query(Member).filter(Member.email == email).first

    if existing_member:
        return {
            "message": "Email already exists"
        }

    member = Member(
        name = name,
        email = email,
        address = address,
        phone = phone,
        status = status
    )

    db.add(member)
    db.commit()

    return RedirectResponse(
        url="/members",
        status_code=303
    )

