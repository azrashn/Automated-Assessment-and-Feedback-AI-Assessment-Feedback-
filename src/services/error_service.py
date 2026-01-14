from sqlalchemy.orm import Session
from src.repositories.error_repo import ErrorReportRepository
from src.models.report import ErrorReport
from src.schemas.report import ErrorReportCreate

class ErrorReportService:
    def __init__(self, db: Session):
        self.repo = ErrorReportRepository(db)
    
    def create_report(self, data: ErrorReportCreate):
        rep = ErrorReport(
            student_id=data.student_id,
            description=data.description,
            issue_type=data.issue_type
        )
        self.repo.save(rep)
        return rep