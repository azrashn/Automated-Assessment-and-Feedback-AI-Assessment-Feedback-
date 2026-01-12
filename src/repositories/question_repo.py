class QuestionRepository: 

    def __init__(self, db): 

        self.db = db 

    def add_question(self, q): 

        pass 

    def get_by_id(self, qid): 

        return None 

   def find_questions(self, difficulty: str, skill_category: str):
    return self.db.query(Question).filter(
    Question.difficulty == difficulty,
    Question.skill_category == skill_category,
    Question.is_active == True
    ).all()

    def get_all(self): 

        return []

