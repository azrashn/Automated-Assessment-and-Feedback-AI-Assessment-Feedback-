from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.services.exam_service import ExamService
from src.schemas.exam import AnswerCreate, ExamSubmit, ReportOut
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/start")
def start_exam(
    skill: str, 
    level: str = "A1", 
    user_id: int = Query(...), 
    db: Session = Depends(get_db)
):
    
    service = ExamService(db)
    session, questions = service.start_exam_session(user_id, skill, level)
    
    if not questions:
        raise HTTPException(status_code=404, detail="Soru bulunamadı")
    
    remaining_seconds = 0
    if session.end_time:
        delta = session.end_time - datetime.now()
        remaining_seconds = max(0, int(delta.total_seconds()))
    else:
        remaining_seconds = 1200

    return {
        "session_id": session.session_id,
        "questions": questions,
        "remaining_seconds": remaining_seconds
    }

@router.post("/submit-answer")
def submit_answer(ans: AnswerCreate, session_id: int, db: Session = Depends(get_db)):
    service = ExamService(db)
    service.save_answer(
        session_id=session_id, 
        question_id=ans.question_id, 
        selected_option_id=ans.selected_option_id,
        text_response=ans.text_response
    )
    return {"status": "saved"}

@router.post("/upload-audio")
def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    service = ExamService(db)
    filename = service.save_audio(file)
    return {"filename": filename}

@router.post("/submit", response_model=ReportOut)
def finalize_exam(payload: ExamSubmit, db: Session = Depends(get_db)):
    service = ExamService(db)
    
    if payload.answers:
        for ans in payload.answers:
            service.save_answer(
                session_id=payload.session_id,
                question_id=ans.question_id,
                selected_option_id=ans.selected_option_id,
                text_response=ans.text_response
            )
            
    return service.finalize_exam(payload.session_id, skill_name=payload.skill)
