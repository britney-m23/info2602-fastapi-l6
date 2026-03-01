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
from app.pagination import Pagination

admin_router = APIRouter(tags=["Admin App"])

@admin_router.get("/admin")
def admin_page(
    request: Request,
    db: SessionDep,
    user: AdminDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=100, le=100),
    q: str = Query(default=""),
    done: str = Query(default="any", regex="^(?:true|false|any)$"),
):
    offset = (page - 1) * limit

    # build main selection with optional filters
    stmt = select(Todo).join(User)
    if q:
        stmt = stmt.where(
            Todo.text.ilike(f"%{q}%") | User.username.ilike(f"%{q}%")
        )
    if done != "any":
        stmt = stmt.where(Todo.done == (done == "true"))

    # count with same filters
    count_stmt = select(func.count(Todo.id)).select_from(Todo).join(User)
    if q:
        count_stmt = count_stmt.where(
            Todo.text.ilike(f"%{q}%") | User.username.ilike(f"%{q}%")
        )
    if done != "any":
        count_stmt = count_stmt.where(Todo.done == (done == "true"))

    count_todos = db.exec(count_stmt).one()

    todos = db.exec(stmt.offset(offset).limit(limit)).all()
    pagination = Pagination(total_count=count_todos, current_page=page, limit=limit)

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "current_user": user,
            "todos": todos,
            "pagination": pagination,
            "q": q,
            "done": done,
        },
    )