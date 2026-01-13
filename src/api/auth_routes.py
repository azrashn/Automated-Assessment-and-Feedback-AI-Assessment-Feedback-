from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.services.auth_service import AccountService
from src.schemas.auth import UserCreate, UserLogin

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    FR-1: Öğrenci kaydı oluşturur.
    """
    service = AccountService(db)
    new_student = service.create_account(user)
    
    # Frontend'in hata almaması için basit JSON dönüyoruz
    return {
        "message": "Kayıt Başarılı",
        "user_id": new_student.user_id,
        "email": new_student.email
    }

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    FR-1: Giriş yapar ve yönlendirme bilgisini döner.
    """
    service = AccountService(db)
    u = service.login(user)
    
    # Frontend'in beklediği yanıt formatı
    return {
        "user_id": u.user_id,
        "username": u.username,
        "role": u.role,
        "redirect": "dashboard.html",
        "msg": "Giriş Başarılı"
    }