from pydantic import BaseModel
from typing import Optional, Dict, Any

<<<<<<< HEAD
# FR-20: Hata Bildirimi
=======
# FR-20: Error Reporting
>>>>>>> 2c133b0405c322e5858327577eb313ae7769e837
class ErrorReportCreate(BaseModel):
    student_id: int
    description: str
    issue_type: str

<<<<<<< HEAD
# FR-11: AI Geri Bildirimi
=======
# FR-11: AI Feedback
>>>>>>> 2c133b0405c322e5858327577eb313ae7769e837
class ReportOut(BaseModel):
    overall_score: float
    feedback: str
    breakdown: Optional[Dict[str, float]] = {}

<<<<<<< HEAD
# FR-19: Güvenlik Logu
=======
# FR-19: Security Log
>>>>>>> 2c133b0405c322e5858327577eb313ae7769e837
class ThreatLogCreate(BaseModel):
    details: str

class PolicyOut(BaseModel):
    policy_name: str
    is_active: bool