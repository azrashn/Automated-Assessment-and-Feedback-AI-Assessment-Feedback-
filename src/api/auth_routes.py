from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db

router = APIRouter()

@router.post("/register")
def register(db: Session = Depends(get_db)):
    return {"msg": "Register Endpoint Hazır"}

@router.post("/login")
def login(db: Session = Depends(get_db)):
    return {"msg": "Login Endpoint Hazır"}
