from pydantic import BaseModel
from typing import Optional, Dict, Any

# FR-20: Error Reporting
class ErrorReportCreate(BaseModel):
    student_id: int
    description: str
    issue_type: str

# FR-11: AI Feedback
class ReportOut(BaseModel):
    overall_score: float
    feedback: str
    breakdown: Optional[Dict[str, float]] = {}

# FR-19: Security Log
class ThreatLogCreate(BaseModel):
    details: str

class PolicyOut(BaseModel):
    policy_name: str
    is_active: bool