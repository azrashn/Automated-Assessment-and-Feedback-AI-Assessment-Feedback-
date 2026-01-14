from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from src.database import get_db

# Modeller (Senin attığın dosyadaki isimler)
from src.models.exam import ExamSession, Answer, Question, QuestionOption
from src.models.user import User, LevelRecord # Kullanıcı tablon nerede tanımlıysa orası
# Not: Eğer User modelin 'src.models.user' içinde değilse orayı düzeltmelisin.

from src.schemas.report import ErrorReportCreate
from src.services.error_service import ErrorReportService
from src.utils.error_handler import check_found

router = APIRouter()

# --- 1. HATA BİLDİRİMİ ---
@router.post("/issue")
def report_issue(rep: ErrorReportCreate, db: Session = Depends(get_db)):
    service = ErrorReportService(db)
    service.create_report(rep)
    return {"status": "reported", "msg": "Bildirim alındı"}

# --- 2. DASHBOARD ---
@router.get("/dashboard/{user_id}")
def get_dashboard_stats(user_id: int, db: Session = Depends(get_db)):
    # Öğrenci/User modelinin yolu projende farklı olabilir, burayı kontrol et:
    # Student tablosunu kullanıyorsan Student, User kullanıyorsan User.
    # Örnek olarak User üzerinden gidiyorum:
    user = db.query(User).filter(User.user_id == user_id).first()
    check_found(user, "Kullanıcı")

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
        "username": user.username if hasattr(user, 'username') else "Öğrenci",
        "completed_exams": completed_count,
        "average_score": round(avg_score, 1),
        "overall_level": overall_level
    }

# --- 3. GEÇMİŞ LİSTESİ ---
@router.get("/history/{user_id}")
def get_user_history(user_id: int, db: Session = Depends(get_db)):
    sessions = db.query(ExamSession).filter(
        ExamSession.student_id == user_id
    ).order_by(ExamSession.start_time.desc()).all()

    return [
        {
            "id": s.session_id,  # Senin modelinde 'session_id'
            "start_time": s.start_time,
            "detected_level": s.detected_level,
            "overall_score": s.overall_score,
            "status": s.status
        }
        for s in sessions
    ]

# --- 4. DETAYLI RAPOR (Analysis Sayfası İçin) ---
@router.get("/detail/{session_id}")
def get_exam_detail(session_id: int, db: Session = Depends(get_db)):
    """
    Frontend analysis.html ile uyumlu çalışacak şekilde verileri hazırlar.
    Senin Answer ve QuestionOption tablolarını kullanarak metinleri bulur.
    """
    session = db.query(ExamSession).get(session_id)
    check_found(session, "Sınav oturumu")

    if session.status not in ["COMPLETED", "EXPIRED"]:
        raise HTTPException(status_code=403, detail="Bu sınav henüz tamamlanmadı.")

    # Cevapları, Soruyu ve Şıkları getir (Performans için joinedload kullandık)
    answers = db.query(Answer).options(
        joinedload(Answer.question).joinedload(Question.options)
    ).filter(Answer.session_id == session_id).all()

    questions_data = []
    correct_count = 0
    wrong_count = 0

    for ans in answers:
        question = ans.question
        
        # 1. Kullanıcının seçtiği metni bul
        user_answer_text = "Boş Bırakıldı"
        if ans.selected_option_id:
            # Sorunun şıkları içinden kullanıcının seçtiği ID'yi buluyoruz
            selected_opt = next((opt for opt in question.options if opt.option_id == ans.selected_option_id), None)
            if selected_opt:
                user_answer_text = selected_opt.content
        
        # 2. Doğru cevabın metnini bul
        correct_opt = next((opt for opt in question.options if opt.is_correct), None)
        correct_answer_text = correct_opt.content if correct_opt else "Belirtilmedi"

        # 3. İstatistik Hesapla
        # Answer tablosunda is_correct zaten var, onu kullanıyoruz
        if ans.is_correct:
            correct_count += 1
        else:
            wrong_count += 1

        questions_data.append({
            "question_text": question.text,
            "user_answer": user_answer_text,
            "correct_answer": correct_answer_text,
            "is_correct": ans.is_correct if ans.is_correct is not None else False
        })

    return {
        "date": session.end_time if session.end_time else session.last_activity,
        "score": session.overall_score,
        "level": session.detected_level,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "ai_feedback": "Detaylı analiz henüz oluşturulmadı.", 
        "questions": questions_data
    }