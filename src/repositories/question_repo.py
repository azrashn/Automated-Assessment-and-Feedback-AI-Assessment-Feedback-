from sqlalchemy.orm import Session
from src.models.exam import Question

class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def add_question(self, q: Question):
        self.db.add(q)
        self.db.commit()
        self.db.refresh(q)
        return q
    
    def get_by_id(self, qid: int):
        return self.db.query(Question).get(qid)
    
    def find_questions(self, difficulty: str, skill_category: str):
        return self.db.query(Question).filter(
            Question.difficulty == difficulty,
            Question.skill_category == skill_category,
            Question.is_active == True
        ).all()
        
    def get_all(self):
        return self.db.query(Question).all()
    
    def delete_question(self, qid: int):
        q = self.db.query(Question).get(qid)
        if q:
            self.db.delete(q)
            self.db.commit()
            return True
        return False
