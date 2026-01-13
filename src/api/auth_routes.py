from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
# Servisler
from src.services.admin_service import AdminService
from src.services.security_service import SecurityService
# Şemalar
from src.schemas.exam import QuestionCreate, ScoreOverride
from src.schemas.report import ThreatLogCreate

router = APIRouter()

# =============================================================================
# BÖLÜM 1: ADMIN İŞLEMLERİ (Soru Ekleme, Puan Düzenleme)
# =============================================================================

@router.post("/question")
def add_question(q: QuestionCreate, db: Session = Depends(get_db)):
    """
    FR-15: Soru havuzuna yeni soru ekler.
    """
    service = AdminService(db)
    return service.manage_question_pool(q)

@router.post("/score-override")
def override_score(data: ScoreOverride, db: Session = Depends(get_db)):
    """
    FR-17: Öğrenci puanını manuel değiştirir.
    """
    service = AdminService(db)
    service.override_score(data.session_id, data.new_score) 
    return {"status": "updated", "msg": "Puan güncellendi"}

# =============================================================================
# BÖLÜM 2: GÜVENLİK YÖNETİMİ (Politikalar ve Loglar)
# =============================================================================

@router.get("/policies", response_model=List[str]) 
def get_policies(db: Session = Depends(get_db)):
    """
    FR-19: Aktif güvenlik kurallarını (örn: copy-paste engeli) çeker.
    """
    service = SecurityService(db)
    return service.fetch_active_rules()

@router.post("/log")
def log_threat(log: ThreatLogCreate, db: Session = Depends(get_db)):
    """
    FR-19: Güvenlik ihlallerini (kopyala-yapıştır denemesi) kaydeder.
    """
    service = SecurityService(db)
    service.log_threat(log.details)
    return {"status": "logged"}