from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException
import random

# IMPORTLAR
from src.repositories.user_repo import UserRepository
from src.schemas.auth import UserCreate, UserLogin

class AccountService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_account(self, data: UserCreate):
        # 1. Email kontrolü
        if self.repo.check_email(data.email):
            raise HTTPException(400, "Email already exists")
        
        # 2. Şifre Hashleme
        hashed = self.pwd_context.hash(data.password)
        
        # 3. Öğrenci Numarası
        st_num = data.student_number or f"ST-{random.randint(10000,99999)}"
        
        # 4. Kayıt (Repository'deki yeni fonksiyonu çağırıyoruz)
        # Not: User(...) nesnesi oluşturup göndermiyoruz, direkt verileri gönderiyoruz.
        return self.repo.create_student(data, hashed, st_num)

    def login(self, data: UserLogin):
        u = self.repo.find_user_by_email(data.email)
        if not u or not self.pwd_context.verify(data.password, u.password_hash):
            raise HTTPException(401, "Invalid credentials")
        return u