from sqlalchemy.orm import Session
from src.models.exam import Question
from src.repositories.exam_repo import ExamRepository
from src.repositories.question_repo import QuestionRepository
from src.schemas.exam import QuestionCreate

class AdminService:
    def __init__(self, db: Session):
        self.q_repo = QuestionRepository(db)
        self.ex_repo = ExamRepository(db)

    def manage_question_pool(self, data: QuestionCreate):
        # Admin yeni soru ekler
        q = Question(
            text=data.text, 
            type=data.type, 
            difficulty=data.difficulty, 
            skill_category=data.skill_category
        )
        return self.q_repo.add_question(q)
    
    def override_score(self, session_id: int, new_score: float):
        # Admin bir öğrencinin puanını manuel değiştirir (FR-17)
        sess = self.ex_repo.get_session(session_id)
        if sess:
            sess.overall_score = new_score
            self.ex_repo.db.commit()