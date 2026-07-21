# from fastapi import APIRouter, Depends, HTTPException
# from database import sessionLocal
# from typing import Annotated
# from sqlalchemy.orm import Session
# from router.auth import get_current_user
# from models import Todos

# router = APIRouter()


# def get_db():
#     db = sessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# db_dependency = Annotated[Session, Depends(get_db)]
# user_dependency = Annotated[dict, Depends(get_current_user)]


# @router.get("/admin/todos")
# def get_todos_by_admin(db: db_dependency, user: user_dependency):
#     if user is None or user.get("role") != "Admin":
#         raise HTTPException(status_code=404, detail="Failed Authentication!")
#     return db.query(Todos).all()


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
