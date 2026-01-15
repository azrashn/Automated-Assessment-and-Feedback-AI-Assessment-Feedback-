from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.services.auth_service import AccountService
from src.schemas.auth import UserCreate, UserLogin, UserUpdate # UserUpdate eklendi

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    FR-1: Öğrenci kaydı oluşturur.
    """
    service = AccountService(db)
    new_student = service.create_account(user)
    
    return {
        "message": "Registration Successful", 
        "user_id": new_student.user_id,
        "email": new_student.email
    }

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    FR-1: Giriş yapar.
    """
    service = AccountService(db)
    u = service.login(user)
    
    # Redirection Logic
    redirect_url = "/dashboard.html"
    if u.role in ["admin", "administrator"]:
        redirect_url = "/admin.html"

    return {
        "user_id": u.user_id,
        "username": u.username,
        "role": u.role,
        "redirect": redirect_url,
        "msg": "Login Successful" 
    }

# =============================================================================
# FR-2: PROFILE OPERATIONS
# =============================================================================

@router.get("/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    """Profil sayfasında gösterilecek kullanıcı bilgilerini döner."""
    service = AccountService(db)
    user = service.get_user_profile(user_id)
    
    # Manually creating dictionary to avoid leaking password hashes
    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "is_admin": user.role in ["admin", "administrator"]
    }

@router.put("/profile/{user_id}")
def update_profile(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    """Updates the username or email address."""
    service = AccountService(db)
    updated_user = service.update_profile(user_id, data)
    
    return {
        "status": "success", 
        "msg": "Profile updated successfully.", 
        "username": updated_user.username,
        "email": updated_user.email
    }

@router.delete("/profile/{user_id}")
def delete_account(user_id: int, db: Session = Depends(get_db)):
    """Kullanıcının kendi hesabını silmesini sağlar."""
    service = AccountService(db)
    success = service.delete_account(user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Delete operation failed.") 
        
    return {"status": "deleted", "msg": "Your account has been successfully deleted."} 
