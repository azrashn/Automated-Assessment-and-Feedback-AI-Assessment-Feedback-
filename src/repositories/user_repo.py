from sqlalchemy.orm import Session
from src.models.user import User, Student, LevelRecord
# Şema importunu servisten gelen veriye uyumlu hale getirdik
from src.schemas.auth import UserCreate 

class UserRepository:
    def __init__(self, db):
        self.db = db

    def create_student(self, user_data, hashed_password, student_number):
        # Student nesnesi oluşturduğumuzda User tablosu OTOMATİK dolar.
        new_student = Student(
            username=user_data.fullname,  # Fullname'i username olarak kullanıyoruz
            email=user_data.email,
            password_hash=hashed_password,
            is_active=True,
            role="student",
            student_number=student_number
        )
        
        self.db.add(new_student)
        self.db.flush() # ID oluşması için flush (commit değil)
        
        # Level kaydını oluştur
        level = LevelRecord(
            student_id=new_student.user_id,
            reading_level=None,
            writing_level=None,
            listening_level=None,
            speaking_level=None,
            overall_level="A1" # Genel seviye A1 başlayabilir, sorun yok
        )
        self.db.add(level)
        
        self.db.commit()
        self.db.refresh(new_student)
        return new_student

    def check_email(self, email):
        return self.db.query(User).filter(User.email == email).first() is not None

    def find_user_by_email(self, email):
        return self.db.query(User).filter(User.email == email).first()

    def find_user_by_id(self, uid):
        return self.db.query(User).get(uid)