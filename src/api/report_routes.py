from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db

router = APIRouter()

@router.post("/issue")
def report_issue(db: Session = Depends(get_db)):
    return {"status": "reported"}

@router.get("/dashboard/{user_id}")
def get_dashboard_stats(user_id: int, db: Session = Depends(get_db)):
    return {"msg": "Dashboard Stats"}

@router.get("/history/{user_id}")
def get_user_history(user_id: int, db: Session = Depends(get_db)):
    return []
