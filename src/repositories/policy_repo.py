from sqlalchemy.orm import Session
from src.models.security import SecurityPolicy, SecurityLog

class PolicyRepository: 

 def __init__(self, db: Session):
  self.db = db 

 def query_rules(self): 
  return self.db.query(SecurityPolicy).filter(SecurityPolicy.is_active == True).all()

 def insert_log_record(self, log: SecurityLog): 
  self.db.add(log)
  self.db.commit()