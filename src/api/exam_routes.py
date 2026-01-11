from fastapi import APIRouter, Depends, UploadFile 
from sqlalchemy.orm import Session 
from src.database import get_db 

router = APIRouter() 

@router.get("/start") 

def start_exam(db: Session = Depends(get_db)): 

    return {"msg": "Start Exam Hazır"} 

@router.post("/submit-answer") 

def submit_answer(db: Session = Depends(get_db)): 

    return {"status": "saved"} 

@router.post("/upload-audio") 

def upload_audio(file: UploadFile, db: Session = Depends(get_db)): 

    return {"filename": "test.webm"} 

@router.post("/submit") 

def finalize_exam(db: Session = Depends(get_db)): 

    return {"score": 0} 
