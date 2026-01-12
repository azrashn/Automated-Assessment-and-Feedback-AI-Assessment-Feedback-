from src.database import Base 
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Question(Base): 

    __tablename__ = "questions" 

    pass 

class QuestionOption(Base): 

    __tablename__ = "question_options" 

    pass 

class ExamSession(Base): 
    __tablename__ = "exam_sessions" 

    session_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.user_id"))
    
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    
    end_time = Column(DateTime(timezone=True), nullable=True) # Sınavın zorunlu bitiş saati
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) # Son işlem zamanı
 

    status = Column(String(20), default="IN_PROGRESS") # IN_PROGRESS, COMPLETED, ABANDONED, EXPIRED
    overall_score = Column(Float, default=0.0)
    detected_level = Column(String(10), nullable=True)
    is_final = Column(Boolean, default=False) 
    
    student = relationship("src.models.user.Student", back_populates="exam_sessions")
    answers = relationship("Answer", back_populates="session", cascade="all, delete-orphan")
    feedback = relationship("src.models.report.FeedbackReport", back_populates="session", uselist=False)

    

class Answer(Base): 
    __tablename__ = "answers" 

    answer_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.session_id"))
    question_id = Column(Integer, ForeignKey("questions.question_id"))
    selected_option_id = Column(Integer, ForeignKey("question_options.option_id"), nullable=True)
    content = Column(Text, nullable=True)
    audio_path = Column(String(255), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    listen_count = Column(Integer, default=0)

    session = relationship("ExamSession", back_populates="answers")
    question = relationship("Question", back_populates="answers")
