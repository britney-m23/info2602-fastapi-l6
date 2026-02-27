from fastapi import APIRouter, HTTPException, Depends, Request, Response, Form,  Query
from sqlmodel import select, func
from math import ceil
from app.database import SessionDep
from app.models import *
from app.auth import *
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.utilities import flash
from . import templates


admin_router = APIRouter(tags=["Admin App"])

@admin_router.get("/admin")
def admin_page(request:Request, db:SessionDep, user:AdminDep):
    todos = db.exec(select(Todo)).all()
    
    return templates.TemplateResponse(
        request=request, 
        name="admin.html",
        context={
            "current_user": user,
            "todos": todos
        }
    )