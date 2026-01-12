from fastapi import APIRouter, Depends, UploadFile 
from sqlalchemy.orm import Session 
from src.database import get_db 

router = APIRouter() 

@router.get("/start") 

def start_exam(skill: str, level: str = "A1", user_id: int = Query(...), db: Session = Depends(get_db)):
    
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

def submit_answer(db: Session = Depends(get_db)): 

    return {"status": "saved"} 

@router.post("/upload-audio") 

def upload_audio(file: UploadFile, db: Session = Depends(get_db)): 

    return {"filename": "test.webm"} 

@router.post("/submit") 

def finalize_exam(db: Session = Depends(get_db)): 

    return {"score": 0} 

