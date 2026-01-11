from src.database import Base 

class Question(Base): 

    __tablename__ = "questions" 

    pass 

class QuestionOption(Base): 

    __tablename__ = "question_options" 

    pass 

class ExamSession(Base): 

    __tablename__ = "exam_sessions" 

    pass 

class Answer(Base): 

    __tablename__ = "answers" 

    pass 
