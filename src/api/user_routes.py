from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db

from src.models.user import User, Student, LevelRecord
from src.models.exam import ExamSession 

router = APIRouter(prefix="/api/user", tags=["User"])

@router.get("/profile/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Dashboard için güncel verileri çeker.
    Hem Admin hem Öğrenci için çalışır.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    if user.role in ["admin", "administrator"]:
        return {
            "username": user.username,
            "email": user.email,
            "overall_level": "Yönetici",
            "completed_exams": 0,
            "average_score": 0.0,
            "completed_skills": [],
            "is_admin": True
        }

    
    record = db.query(LevelRecord).filter(LevelRecord.student_id == user_id).first()
    
    completed_skills = []
    current_level = "A1"
    
    if record:
        current_level = record.overall_level or "A1"
        
        if record.reading_level: completed_skills.append("reading")
        if record.writing_level: completed_skills.append("writing")
        if record.listening_level: completed_skills.append("listening")
        if record.speaking_level: completed_skills.append("speaking")
    # --------------------------------------------------------

    # İstatistikler (Sayı ve Ortalama)
    exams = db.query(ExamSession).filter(
        ExamSession.student_id == user_id,
        ExamSession.status == "COMPLETED"
    ).all()
    
    avg_score = 0
    if exams:
        total = sum([e.overall_score for e in exams])
        avg_score = round(total / len(exams), 1)

    return {
        "username": user.username,
        "email": user.email,
        "overall_level": current_level,
        "completed_exams": len(exams),
        "average_score": avg_score,
        "completed_skills": completed_skills,
        "is_admin": False
    }

@router.post("/reset-cycle")
def reset_user_cycle(user_id: int = Query(...), db: Session = Depends(get_db)):
    """
    Kullanıcı 4 sınavı tamamladığında döngüyü sıfırlar.
    LevelRecord'daki verileri temizler ama ExamSession geçmişini tutar.
    """
    # 1. Kaydı bul
    record = db.query(LevelRecord).filter(LevelRecord.student_id == user_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")

    # 2. Seviyeleri Sıfırla (Böylece dashboard'daki kilitler açılır)
    record.reading_level = None
    record.writing_level = None
    record.listening_level = None
    record.speaking_level = None
    # overall_level'i sıfırlamıyoruz ki kullanıcı en son hangi seviyede kaldığını bilsin
    
    db.commit()
     
    return {"status": "reset", "msg": "Yeni sınav dönemi başlatıldı."}