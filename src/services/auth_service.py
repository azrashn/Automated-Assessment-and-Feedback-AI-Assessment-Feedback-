from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException
import random

# IMPORTLAR
from src.models.user import User 
from src.repositories.user_repo import UserRepository
# Sadece gerekli şemaları import ediyoruz (UserPasswordUpdate YOK)
from src.schemas.auth import UserCreate, UserLogin, UserUpdate

class AccountService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_account(self, data: UserCreate):
        """
        FR-1: Yeni öğrenci kaydı oluşturur.
        """
        # 1. Email kontrolü
        if self.repo.check_email(data.email):
            raise HTTPException(400, "Email already exists")
        
        # 2. Şifre Hashleme
        hashed = self.pwd_context.hash(data.password)
        
        # 3. Öğrenci Numarası oluşturma
        st_num = data.student_number or f"ST-{random.randint(10000,99999)}"
        
        # 4. Repository'e gönder (User -> Student -> LevelRecord oluşturulacak)
        return self.repo.create_student(data, hashed, st_num)

    def login(self, data: UserLogin):
        """
        FR-1: Kullanıcı girişi.
        """
        u = self.repo.find_user_by_email(data.email)
        
        # 1. Kullanıcı Var mı ve Şifre Doğru mu?
        if not u or not self.pwd_context.verify(data.password, u.password_hash):
            raise HTTPException(401, "Incorrect email or password.")
        
        # 2. HESAP AKTİF Mİ? (FR-18)
        if not u.is_active:
                       raise HTTPException(
                status_code=403, 
                detail="Your account has been suspended by the administrator. Please contact support."
            )
            
        return u

    # =========================================================================
    # FR-2: PROFİL YÖNETİMİ
    # =========================================================================

    def get_user_profile(self, user_id: int):
        """Kullanıcı bilgilerini getirir."""
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(404, "User not found.")
        return user

    def update_profile(self, user_id: int, data: UserUpdate):
        """
        Kullanıcı adı veya E-posta güncellemesi yapar.
        Çakışma (Collision) kontrolü içerir.
        """
        user = self.get_user_profile(user_id)

        # 1. Kullanıcı Adı Değişikliği İsteği Varsa
        if data.username and data.username != user.username:
            # Başka bir kullanıcı bu ismi kullanıyor mu?
            existing_user = self.db.query(User).filter(
                User.username == data.username, 
                User.user_id != user_id # Kendisi hariç
            ).first()
            
            if existing_user:
                raise HTTPException(400, "This username is already taken.")
            
            user.username = data.username

        # 2. E-posta Değişikliği İsteği Varsa
        if data.email and data.email != user.email:
            # Başka bir kullanıcı bu emaili kullanıyor mu?
            existing_email = self.db.query(User).filter(
                User.email == data.email,
                User.user_id != user_id # Kendisi hariç
            ).first()

            if existing_email:
                raise HTTPException(400, "This email address is already in use.")
            
            user.email = data.email

        # 3. Değişiklikleri Kaydet
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise HTTPException(500, f"Update error: {str(e)}")

    def delete_account(self, user_id: int):
        """Kullanıcının kendi hesabını silmesini sağlar."""
        return self.repo.delete_user(user_id)