from src.database import Base

class FeedbackReport(Base):
    __tablename__ = "feedback_reports"
    pass

class ErrorReport(Base):
    __tablename__ = "error_reports"
    pass
