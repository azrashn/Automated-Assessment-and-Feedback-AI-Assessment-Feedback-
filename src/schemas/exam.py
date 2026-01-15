from pydantic import BaseModel
from typing import List, Optional, Dict

class OptionOut(BaseModel):
    option_id: int
    content: str
    class Config:
        from_attributes = True

class QuestionOut(BaseModel):
    question_id: int
    text: str
    type: str
    skill_category: str
    media_url: Optional[str] = None
    options: List[OptionOut] = []
    
    class Config:
        from_attributes = True

class AnswerCreate(BaseModel):
    question_id: int
    selected_option_id: Optional[int] = None
    text_response: Optional[str] = None

class ExamSubmit(BaseModel):
    session_id: int
    answers: List[AnswerCreate] = []
    skill: str = None

class ReportOut(BaseModel):
    overall_score: float
    feedback: str
    breakdown: Optional[Dict[str, float]] = {}

class OptionCreate(BaseModel):
    content: str
    is_correct: bool

class QuestionCreate(BaseModel):
    text: str
    type: str       # MULTIPLE_CHOICE, WRITING, etc.
    difficulty: str # A1, A2, B1...
    skill_category: str
    media_url: Optional[str] = None
    options: List[OptionCreate] = []

class ScoreOverride(BaseModel):
    session_id: int
    new_score: float
    reason: str
