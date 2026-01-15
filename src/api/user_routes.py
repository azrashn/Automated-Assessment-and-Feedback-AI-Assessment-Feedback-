from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.database import get_db

# Modeller
# DÜZELTME 1: User modelini de import ediyoruz
from src.models.user import User, Student, LevelRecord
from src.models.exam import ExamSession 

router = APIRouter(prefix="/api/user", tags=["User"])

@router.get("/profile/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Dashboard için güncel verileri çeker.
    Hem Admin hem Öğrenci için çalışır.
    """
    # 1. DÜZELTME: Doğrudan Student değil, User sorguluyoruz (Polymorphic hata almamak için)
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    # 2. DÜZELTME: Admin Kontrolü
    # Eğer kullanıcı Admin ise istatistik hesaplamaya gerek yok, admin verisi dön.
    if user.role in ["admin", "administrator"]:
        return {
            "username": user.username,
            "email": user.email,
            "overall_level": "Yönetici",
            "completed_exams": 0,
            "average_score": 0.0,
            "completed_skills": [], # Adminin sınavı olmaz
            "is_admin": True # Frontend admin panel butonu gösterebilir
        }

    # 3. ÖĞRENCİ İŞLEMLERİ (Mevcut kodun korunduğu yer)
    # User nesnesi zaten elimizde, ama ilişkiler için Student tablosu üzerinden gitmek gerekebilir
    # veya user_id ile direkt tablolardan çekebiliriz.
    
    # LevelRecord Tablosundan EN GÜNCEL Seviyeyi Çek
    record = db.query(LevelRecord).filter(LevelRecord.student_id == user_id).first()
    
    # --- YENİ EKLENEN KISIM: Tamamlanan Modülleri Listele ---
    completed_skills = []
    current_level = "A1"
    
    if record:
        current_level = record.overall_level or "A1"
        
        # Veritabanında notu girilmiş (None olmayan) yetenekleri listeye ekle
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