from fastapi import FastAPI, Depends, HTTPException  # Added Depends here
import models
from sqlalchemy.orm import Session  # Capitalized Session
from database import engine, sessionLocal
from typing import Annotated, Optional
from models import Todos
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from router import auth
app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)

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


@app.get("/")
def get_todos(db: db_dependency):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}")
def get_todos(db: db_dependency, todo_id: int):

    specific_todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if specific_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!!")
    else:
        return specific_todo


@app.post("/create")
def create_todos(db: db_dependency, newTodo: Todo):
    todo_model = Todos(**newTodo.model_dump())
    db.add(todo_model)
    db.commit()


@app.put("/update/{todo_id}")
def update_todos(db: db_dependency, todo_id: int, update_todo: UpdateTodo):

    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!!")
    update_data = update_todo.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(todo, key, value)
    db.commit()
    return {"message": "Todo updated successfully", "updated_fields": update_data}


@app.delete("/delete/{todo_id}")
def delete_todos(db: db_dependency, todo_id: int):

    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found!!")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
    return {"message": "Todo Deleted successfully"}
