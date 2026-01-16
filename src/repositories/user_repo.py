from sqlalchemy.orm import Session
from src.models.user import User, Student, LevelRecord
from src.schemas.auth import UserCreate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def check_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()
    
    def find_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all_users(self):
        return self.db.query(User).order_by(User.user_id.desc()).all()

    def delete_user(self, user_id: int):
        user = self.db.query(User).get(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

    def create_student(self, user_data: UserCreate, password_hash: str, student_number: str):

        try:
            # User'a ait bilgileri (username, email, password) de buraya veriyoruz.
            db_student = Student(
                username=user_data.username,
                email=user_data.email,
                password_hash=password_hash,
                is_active=True,
                role="student",
                student_number=student_number
            )
            
            self.db.add(db_student)
            self.db.flush() # ID oluşması için flush (db_student.user_id oluşur)

            # Level Kaydı
            db_level = LevelRecord(
                student_id=db_student.user_id,
                overall_level="A1" # Sadece genel seviye görünsün
            )
            self.db.add(db_level)
            
            self.db.commit()
            self.db.refresh(db_student)
            return db_student
            
        except Exception as e:
            self.db.rollback()
            raise e