from sqlalchemy.orm import Session
from src.models.report import ErrorReport


class ErrorReportRepository:
    def __init__(self, db):
        self.db = db

    def save(self, report: ErrorReport):
        self.db.add(report) 
        self.db.commit()
        self.db.refresh(report)
        return report