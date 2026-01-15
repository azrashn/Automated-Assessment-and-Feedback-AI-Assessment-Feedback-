from pydantic import BaseModel
from typing import Optional, Dict, Any

# FR-20: Hata Bildirimi
class ErrorReportCreate(BaseModel):
    student_id: int
    description: str
    issue_type: str

# FR-11: AI Geri Bildirimi
class ReportOut(BaseModel):
    overall_score: float
    feedback: str
    breakdown: Optional[Dict[str, float]] = {}

# FR-19: Güvenlik Logu
class ThreatLogCreate(BaseModel):
    details: str

class PolicyOut(BaseModel):
    policy_name: str
    is_active: bool