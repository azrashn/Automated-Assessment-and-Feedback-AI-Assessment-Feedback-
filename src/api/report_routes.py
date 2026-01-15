from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from src.database import get_db

from src.models.exam import ExamSession, Answer, Question, QuestionOption
from src.models.user import User, LevelRecord 

from src.schemas.report import ErrorReportCreate
from src.services.error_service import ErrorReportService
from src.utils.error_handler import check_found

router = APIRouter()

# Hata Bildirimi
@router.post("/issue")
def report_issue(rep: ErrorReportCreate, db: Session = Depends(get_db)):
    service = ErrorReportService(db)
    service.create_report(rep)
    return {"status": "reported", "msg": "Report received"}

# Dashboard İstatistikleri
@router.get("/dashboard/{user_id}")
def get_dashboard_stats(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    check_found(user, "User")

    completed_count = db.query(ExamSession).filter(
        ExamSession.student_id == user_id,
        ExamSession.status == "COMPLETED"
    ).count()

    avg_score = db.query(func.avg(ExamSession.overall_score)).filter(
        ExamSession.student_id == user_id,
        ExamSession.status == "COMPLETED"
    ).scalar() or 0.0

    level_record = db.query(LevelRecord).filter(LevelRecord.student_id == user_id).first()
    overall_level = level_record.overall_level if level_record else "A1"

    return {
        "username": user.username if hasattr(user, 'username') else "Student",
        "completed_exams": completed_count,
        "average_score": round(avg_score, 1),
        "overall_level": overall_level
    }

# Sınav Geçmişi
@router.get("/history/{user_id}")
def get_user_history(user_id: int, db: Session = Depends(get_db)):
    sessions = db.query(ExamSession).filter(
        ExamSession.student_id == user_id
    ).order_by(ExamSession.start_time.desc()).all()

    return [
        {
            "id": s.session_id,
            "start_time": s.start_time,
            "detected_level": s.detected_level,
            "overall_score": s.overall_score,
            "status": s.status
        }
        for s in sessions
    ]

# Detaylı Sınav Raporu
@router.get("/detail/{session_id}")
def get_exam_detail(session_id: int, db: Session = Depends(get_db)):
    """
    Bu fonksiyon, frontend'deki analysis.html sayfası ile uyumlu olacak şekilde sınav detaylarını hazırlar.
    """
    session = db.query(ExamSession).get(session_id)
    check_found(session, "Exam session")

    if session.status not in ["COMPLETED", "EXPIRED"]:
        raise HTTPException(status_code=403, detail="This exam is not completed yet.")

    # Sınav oturumundaki tüm cevapları veritabanından çek
    answers = db.query(Answer).options(
        joinedload(Answer.question).joinedload(Question.options)
    ).filter(Answer.session_id == session_id).all()

    questions_data = []
    correct_count = 0
    wrong_count = 0

    for ans in answers:
        question = ans.question
        
        # Kullanıcının verdiği cevabı belirle
        user_answer_text = "No answer"
        if ans.selected_option_id:
            # Çoktan seçmeli soru için
            selected_opt = next((opt for opt in question.options if opt.option_id == ans.selected_option_id), None)
            if selected_opt: user_answer_text = selected_opt.content
        else:
            # Açık uçlu soru için (yazılı veya konuşma)
            # Eğer content doluysa, konuşma transkripti burada
            # Boşsa, text_response alanına bak
            if ans.content:
                user_answer_text = ans.content
            elif hasattr(ans, 'text_response') and ans.text_response:
                user_answer_text = ans.text_response
        
        # Doğru cevabı belirle
        correct_opt = next((opt for opt in question.options if opt.is_correct), None)
        correct_answer_text = correct_opt.content if correct_opt else "AI Evaluation"

        # İstatistikleri güncelle
        if ans.is_correct: correct_count += 1
        else: wrong_count += 1

        questions_data.append({
            "question_text": question.text,
            "user_answer": user_answer_text,
            "correct_answer": correct_answer_text,
            "is_correct": ans.is_correct if ans.is_correct is not None else False
        })

    # Sabit metin yerine veritabanındaki AI geri bildirimini kullan
    feedback_text = getattr(session, 'ai_feedback', None)
    
    # Eski sınavlar için AI analizi mevcut değilse
    if not feedback_text:
        feedback_text = "This exam is old, so AI analysis is not available. You can see the analysis by taking a new exam."

    return {
        "date": session.end_time if session.end_time else session.last_activity,
        "score": session.overall_score,
        "level": session.detected_level,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "ai_feedback": feedback_text,
        "questions": questions_data
    }