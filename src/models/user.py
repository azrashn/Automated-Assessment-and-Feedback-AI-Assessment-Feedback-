from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    
    # DİKKAT: seed.py dosyasında 'hashed_password' kullanıyorduk,
    # burada 'password_hash' yapmışsın. seed.py'yi buna göre düzelteceğim.
    password_hash = Column(String(255), nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Polimorfizm için ayrıştırıcı sütun
    role = Column(String(20), default="student")

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role
    }

class Student(User):
    __tablename__ = "students"

    # User tablosundaki user_id ile eşleşiyor (PK + FK)
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    
    student_number = Column(String(20), unique=True, nullable=True)

    # İlişkiler
    level_record = relationship("LevelRecord", back_populates="student", uselist=False)
    
    # String referansları (Circular Import'u önlemek için)
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
    
    # Seviye atamaları (String uzunlukları eklendi - MySQL için şart)
    reading_level = Column(String(5), default="A1")
    writing_level = Column(String(5), default="A1")
    listening_level = Column(String(5), default="A1")
    speaking_level = Column(String(5), default="A1")
    overall_level = Column(String(5), default="A1")
    
    student = relationship("Student", back_populates="level_record")