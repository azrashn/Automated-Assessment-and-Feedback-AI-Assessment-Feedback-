from sqlalchemy.orm import Session
from src.repositories.policy_repo import PolicyRepository
from src.models.security import SecurityLog

class SecurityService:
    def __init__(self, db: Session):
        self.repo = PolicyRepository(db)

    def fetch_active_rules(self):
        policies = self.repo.query_rules()
        # SQL tablosunda policy_name demiştik
        return [p.policy_name for p in policies]

    def log_threat(self, details: str):
        log = SecurityLog(details=details)
        self.repo.insert_log_record(log)