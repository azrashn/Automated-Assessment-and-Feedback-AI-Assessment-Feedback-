from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON
from sqlalchemy.sql import func
from src.database import Base 

class SecurityLog(Base): 
  __tablename__ = "security_logs" 
  
  # FR-19: Kopyala/Yapıştır ihlalleri buraya loglanır
  log_id = Column(Integer, primary_key=True, index=True)
  details = Column(Text)
  timestamp = Column(DateTime(timezone=True), server_default=func.now())

class SecurityPolicy(Base): 
  __tablename__ = "security_policies" 
  policy_id = Column(Integer, primary_key=True, index=True)
  # SQL tablosuyla uyumlu
  policy_name = Column(String(50), unique=True) 
  is_active = Column(Boolean, default=True)
  # FR-19: Politika detayları (örn: {"block_paste": true, "browser_lock": false})
  config_json = Column(JSON, nullable=True)