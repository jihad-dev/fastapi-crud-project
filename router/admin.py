from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import sessionLocal
from models import Todos
from router.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todos", status_code=status.HTTP_200_OK)
def get_todos_by_admin(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    if user.get("role") != "Admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin privileges required",
        )

    return db.query(Todos).all()


@router.delete("/delete/{todo_id}", status_code=status.HTTP_200_OK)
def delete_todo_by_admin(user: user_dependency, db: db_dependency, todo_id: int):
    # 1. Authentication Check (Missing/Invalid Token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # 2. Authorization Check (Role Permission)
    if user.get("role") != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin privileges required",
        )

    # 3. Fetch item from DB
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found!"
        )

    # 4. Perform single instance delete
    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted successfully"}
