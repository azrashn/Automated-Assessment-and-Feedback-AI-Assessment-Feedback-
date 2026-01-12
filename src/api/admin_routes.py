from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db

router = APIRouter()

@router.post("/question")
def add_question(db: Session = Depends(get_db)):
    return {"status": "ok"}

@router.post("/score-override")
def override_score(db: Session = Depends(get_db)):
    return {"status": "updated"}
