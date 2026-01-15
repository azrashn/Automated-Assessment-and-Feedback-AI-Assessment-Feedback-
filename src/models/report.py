from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base

class FeedbackReport(Base):
    __tablename__ = "feedback_reports"

    report_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.session_id"))
    
    # FR-11 & Analysis Use Case: Detailed feedback coming from the AI Module
    recommendations = Column(Text)
    overall_score = Column(Float)
    score_breakdown = Column(JSON) # {reading: 80, writing: 70...}
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("src.models.exam.ExamSession", back_populates="feedback")

class ErrorReport(Base):
    __tablename__ = "error_reports"
    
    # FR-20: Reporting technical issues
    report_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.user_id"))
    description = Column(Text)      # Detail of the issue
    issue_type = Column(String(50)) # Audio issue, Video issue, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    student = relationship("src.models.user.Student", back_populates="error_reports")