from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Any

from src.database import get_db
from src.services.admin_service import AdminService
from src.services.security_service import SecurityService
from src.schemas.exam import QuestionCreate, ScoreOverride
from src.schemas.report import ThreatLogCreate

router = APIRouter()

@router.post("/question")
def add_question(q: QuestionCreate, db: Session = Depends(get_db)):
    """FR-15: Adds a new question to the question pool."""
    service = AdminService(db)
    return service.manage_question_pool(q)

@router.get("/questions")
def list_questions(db: Session = Depends(get_db)):
    """Lists all questions."""
    service = AdminService(db)
    questions = service.get_all_questions()
    return [
        {
            "question_id": q.question_id,
            "text": q.text,
            "type": q.type,
            "difficulty": q.difficulty,
            "skill_category": q.skill_category
        }
        for q in questions
    ]

@router.delete("/question/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """FR-15: Deletes a question."""
    service = AdminService(db)
    success = service.remove_question(question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"status": "deleted", "msg": "Question deleted."}

@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    """Lists all users."""
    service = AdminService(db)
    users = service.get_all_users()
    return [
        {
            "user_id": u.user_id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "joined_at": u.created_at.strftime("%Y-%m-%d") if u.created_at else "-"
        }
        for u in users
    ]

@router.post("/user/{user_id}/toggle-status")
def toggle_user_status(user_id: int, db: Session = Depends(get_db)):
    """FR-18: Freezes or activates the user account."""
    service = AdminService(db)
    new_status = service.toggle_user_status(user_id)
    
    if new_status is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    msg = "Account activated." if new_status else "Account frozen."
    return {"status": "success", "msg": msg, "is_active": new_status}

@router.delete("/user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """FR-18: Completely deletes the user."""
    service = AdminService(db)
    success = service.remove_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "deleted", "msg": f"User {user_id} deleted."}

@router.get("/sessions")
def list_exam_sessions(db: Session = Depends(get_db)):
    service = AdminService(db)
    data = service.get_all_exam_sessions()
    
    return [
        {
            "session_id": s.session_id,
            "student_id": s.student_id,
            "student_name": username if username else "Unknown",
            "score": s.overall_score,
            "level": s.detected_level,
            "date": s.end_time if s.end_time else s.start_time,
            "status": s.status
        }
        for s, username in data
    ]

@router.post("/score-override")
def override_score(data: ScoreOverride, db: Session = Depends(get_db)):
    """FR-17: Allows the admin to manually override a student's score."""
    service = AdminService(db)
    service.override_score(data.session_id, data.new_score) 
    return {"status": "updated", "msg": "Score successfully updated"}

@router.get("/policies", response_model=List[str]) 
def get_policies(db: Session = Depends(get_db)):
    """Lists active security policies."""
    service = SecurityService(db)
    return service.fetch_active_rules()

@router.post("/log")
def log_threat(log: ThreatLogCreate, db: Session = Depends(get_db)):
    """Logs threats detected by the client."""
    service = SecurityService(db)
    service.log_threat(log.details)
    return {"status": "logged"}

@router.get("/reports")
def list_reports(db: Session = Depends(get_db)):
    """FR-20: Lists all error reports."""
    service = AdminService(db)
    reports = service.get_all_reports()
    
    # Formatting for frontend table
    return [
        {
            "report_id": r.report_id,
            "student_name": username if username else "Unknown",
            "issue_type": r.issue_type,
            "description": r.description,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "-"
        }
        for r, username in reports
    ]

@router.delete("/report/{report_id}")
def resolve_report(report_id: int, db: Session = Depends(get_db)):
    """FR-20: Marks the issue as resolved (deletes it)."""
    service = AdminService(db)
    success = service.resolve_report(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"status": "resolved", "msg": "Issue resolved."}