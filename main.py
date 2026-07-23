from fastapi import FastAPI, Depends, HTTPException  # Added Depends here
import models
from sqlalchemy.orm import Session  # Capitalized Session
from database import engine, sessionLocal
from typing import Annotated, Optional
from models import Todos
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from router import auth, admin
from router.auth import get_current_user

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(admin.router)


class Todo(BaseModel):
    id: int
    title: str
    description: str = Field(max_length=100)
    priority: int = Field(gt=0, lt=6)
    completed: bool


class UpdateTodo(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = Field(default=None, max_length=100)
    priority: Optional[int] = Field(default=None, gt=0, lt=6)
    completed: Optional[bool] = None


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@app.get("/")
def Home():
    return "Hello Next Level Developer💀"


@app.get("/todos")
def get_todos(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found!")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@app.get("/todo/{todo_id}")
def get_todos_by_id(user: user_dependency, db: db_dependency, todo_id: int):
    if user is None:
        raise HTTPException(status_code=404, detail="Failed Authentication!")
    specific_todo = (
        db.query(Todos)
        .filter(Todos.owner_id == user.get("id"))
        .filter(Todos.id == todo_id)
        .first()
    )
    if specific_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!!")
    else:
        return specific_todo


@app.post("/create")
def create_todos(user: user_dependency, db: db_dependency, newTodo: Todo):
    if user is None:
        raise HTTPException(status_code=404, detail="Failed Authentication!")
    todo_model = Todos(**newTodo.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()
    return {"message": "Todo Created successfully"}


@app.put("/update/{todo_id}")
def update_todos(
    user: user_dependency, db: db_dependency, todo_id: int, update_todo: UpdateTodo
):
    if user is None:
        raise HTTPException(status_code=404, detail="Failed Authentication!")
    todo = (
        db.query(Todos)
        .filter(Todos.owner_id == user.get("id"))
        .filter(Todos.id == todo_id)
        .first()
    )
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!!")
    update_data = update_todo.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(todo, key, value)
    db.commit()
    return {"message": "Todo updated successfully", "updated_fields": update_data}


@app.delete("/delete/{todo_id}")
def delete_todos(user: user_dependency, db: db_dependency, todo_id: int):
    if user is None:
        raise HTTPException(status_code=404, detail="Failed Authentication!")
    todo = (
        db.query(Todos)
        .filter(Todos.owner_id == user.get("id"))
        .filter(Todos.id == todo_id)
        .first()
    )
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!!")
    db.query(Todos).filter(Todos.owner_id == user.get("id")).filter(
        Todos.id == todo_id
    ).delete()
    db.commit()
    return {"message": "Todo Deleted successfully"}
