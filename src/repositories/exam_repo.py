from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import func
from datetime import datetime, timedelta
from src.models.exam import ExamSession, Answer, Question
from src.models.user import LevelRecord
from src.models.report import FeedbackReport

class ExamRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_level_record(self, student_id: int):
        return self.db.query(LevelRecord).filter(LevelRecord.student_id == student_id).first()

    def reset_level_record(self, record: LevelRecord):
        record.reading_level = None
        record.writing_level = None
        record.listening_level = None
        record.speaking_level = None
        record.overall_level = "A1"
        self.db.commit()
    
    def get_active_session(self, user_id: int):
        return self.db.query(ExamSession).filter(
            ExamSession.student_id == user_id,
            ExamSession.status == "IN_PROGRESS"
        ).first()

    def create_session(self, student_id: int, level: str, duration_minutes: int = 20):
        
        # Bitiş zamanını şimdiki zaman + dakika olarak hesapla
        calculated_end_time = datetime.now() + timedelta(minutes=duration_minutes)

        sess = ExamSession(
            student_id=student_id, 
            status="IN_PROGRESS", 
            detected_level=level,
            end_time=calculated_end_time  # Bitiş zamanı eklendi
        )
        self.db.add(sess)
        self.db.commit()
        self.db.refresh(sess)
        return sess

    def get_session(self, sid: int):
        return self.db.query(ExamSession).get(sid)

    def mark_session_abandoned(self, session: ExamSession):
        session.status = "ABANDONED"
        session.overall_score = 0.0
        session.end_time = datetime.now()
        self.db.commit()

    def mark_session_expired(self, session: ExamSession):
        session.status = "EXPIRED"
        session.end_time = datetime.now()
        self.db.commit()

    def find_records_by_student_id(self, student_id: int):
        return self.db.query(ExamSession).filter(ExamSession.student_id == student_id).all()

    def get_questions_by_skill(self, skill: str, level: str, limit: int = 10):
        return self.db.query(Question)\
            .options(joinedload(Question.options))\
            .filter(
                Question.skill_category.ilike(skill),
                Question.difficulty == level,
                Question.is_active == True
            )\
            .order_by(func.random())\
            .limit(limit)\
            .all()

    def save_answer(self, session_id: int, question_id: int, selected_option_id: int = None, text_response: str = None):
        existing_ans = self.db.query(Answer).filter(
            Answer.session_id == session_id,
            Answer.question_id == question_id
        ).first()

        if existing_ans:
            existing_ans.selected_option_id = selected_option_id
            existing_ans.content = text_response
        else:
            new_ans = Answer(
                session_id=session_id,
                question_id=question_id,
                selected_option_id=selected_option_id,
                content=text_response
            )
            self.db.add(new_ans)
        
        
        session = self.get_session(session_id)
        if session:
            session.last_activity = func.now()

        self.db.commit()

    def get_answer_by_session_question(self, session_id: int, question_id: int):
        return self.db.query(Answer).filter(
            Answer.session_id == session_id,
            Answer.question_id == question_id
        ).first()
    
    def commit(self):
        self.db.commit()

    def save_final_result(self, session, report):
        pass
