from fastapi import APIRouter

# 1. Correctly initialize as an APIRouter
router = APIRouter()

# 2. Add the '@' symbol to make it a decorator
@router.get("/auth")
def authentication():
    return {"user": "Authenticated"}