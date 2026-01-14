from pydantic import BaseModel

class ErrorReportCreate(BaseModel):
    student_id: int
    description: str
    issue_type: str

class ReportOut(BaseModel):
    overall_score: float
    feedback: str
    breakdown: Optional[Dict[str, float]] = {}

class ThreatLogCreate(BaseModel):
    details: str

class PolicyOut(BaseModel):
    policy_name: str
    is_active: bool
