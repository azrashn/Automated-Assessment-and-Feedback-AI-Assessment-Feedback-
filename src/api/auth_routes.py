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
    FR-1: Giriş yapar ve rolüne göre yönlendirme bilgisini döner.
    """
    service = AccountService(db)
    u = service.login(user)
    
    # --- YÖNLENDİRME MANTIĞI ---
    # Varsayılan rota öğrenci paneli
    redirect_url = "/dashboard.html"
    
    # Eğer rolü admin veya administrator ise admin paneline git
    if u.role in ["admin", "administrator"]:
        redirect_url = "/admin.html" # Admin HTML dosyasının adı neyse o olmalı

    return {
        "user_id": u.user_id,
        "username": u.username,
        "role": u.role,
        "redirect": redirect_url, # Frontend bu adresi kullanacak
        "msg": "Giriş Başarılı"
    }