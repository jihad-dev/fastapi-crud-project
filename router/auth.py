from fastapi import APIRouter, Depends
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import sessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class createUsers(BaseModel):
    email: str
    username: str
    firstname: str
    lastname: str
    password: str
    role: str


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/create_user")
def create_user(db: db_dependency, newUser: createUsers):

    user_model = Users(
        email=newUser.email,
        username=newUser.username,
        firstname=newUser.firstname,
        lastname=newUser.lastname,
        hash_password=bcrypt_context.hash(newUser.password),
        role=newUser.role,
    )

    db.add(user_model)
    db.commit()

    return {"status": "Successful", "message": "User created successfully"}
