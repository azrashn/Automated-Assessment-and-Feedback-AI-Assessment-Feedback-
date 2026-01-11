from src.database import Base 

class SecurityLog(Base): 
  __tablename__ = "security_logs" 
pass 

class SecurityPolicy(Base): 
  __tablename__ = "security_policies" 
pass 