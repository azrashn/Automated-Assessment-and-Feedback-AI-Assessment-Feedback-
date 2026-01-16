from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    
    password_hash = Column(String(255), nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Polimorfizm
    role = Column(String(20), default="student")

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role
    }

class Student(User):
    __tablename__ = "students"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    student_number = Column(String(20), unique=True, nullable=True)

    # İlişkiler
    level_record = relationship("LevelRecord", back_populates="student", uselist=False)
    exam_sessions = relationship("src.models.exam.ExamSession", back_populates="student")
    error_reports = relationship("src.models.report.ErrorReport", back_populates="student")

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

class Administrator(User):
    __tablename__ = "administrators"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    department = Column(String(50), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

class LevelRecord(Base):
    __tablename__ = "level_records"

    record_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.user_id"))
    
    #  DÜZELTME: default="A1" KALDIRILDI.
    reading_level = Column(String(5), nullable=True)
    writing_level = Column(String(5), nullable=True)
    listening_level = Column(String(5), nullable=True)
    speaking_level = Column(String(5), nullable=True)
    
    # Genel seviye varsayılan A1  (görüntüleme için)
    overall_level = Column(String(5), default="A1")
    
    student = relationship("Student", back_populates="level_record")