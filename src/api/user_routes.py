from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db

router = APIRouter(prefix="/api/user", tags=["User"])

@router.get("/profile/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    return {"msg": "Profile Info"}