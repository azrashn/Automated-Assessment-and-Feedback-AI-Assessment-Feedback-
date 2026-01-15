from sqlalchemy.orm import Session
from src.models.exam import Question, QuestionOption, ExamSession
from src.models.user import User, LevelRecord
from src.models.report import ErrorReport  # <-- NEWLY ADDED
from src.repositories.exam_repo import ExamRepository
from src.repositories.question_repo import QuestionRepository
from src.schemas.exam import QuestionCreate
from src.repositories.user_repo import UserRepository

class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.q_repo = QuestionRepository(db)
        self.ex_repo = ExamRepository(db)
        self.u_repo = UserRepository(db)

    # =========================================================================
    # 1. QUESTION MANAGEMENT
    # =========================================================================

    def manage_question_pool(self, data: QuestionCreate):
        """Adds a new question and its options to the question pool."""
        q = Question(
            text=data.text, 
            type=data.type, 
            difficulty=data.difficulty, 
            skill_category=data.skill_category
        )

        if data.options:
            for opt_data in data.options:
                opt = QuestionOption(
                    content=opt_data.content,
                    is_correct=opt_data.is_correct
                )
                q.options.append(opt)
        
        result = self.q_repo.add_question(q)
        return result

    def get_all_questions(self):
        return self.q_repo.get_all()

    def remove_question(self, question_id: int):
        return self.q_repo.delete_question(question_id)

    # =========================================================================
    # 2. USER MANAGEMENT (FR-18 EXISTING)
    # =========================================================================

    def get_all_users(self):
        return self.u_repo.get_all_users()

    def remove_user(self, user_id: int):
        """Permanently deletes the user (Use with caution)."""
        return self.u_repo.delete_user(user_id)

    def toggle_user_status(self, user_id: int):
        """
        FR-18: Freezes or reactivates the user account.
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.is_active = not user.is_active
            try:
                self.db.commit()
                self.db.refresh(user)
                status_text = "Active" if user.is_active else "Passive"
                print(f"👤 User Status Changed: ID {user_id} -> {status_text}")
                return user.is_active
            except Exception as e:
                print(f"❌ Error: {e}")
                self.db.rollback()
                return None
        return None

    # =========================================================================
    # 3. EXAM AND SCORE MANAGEMENT (FR-17 EXISTING)
    # =========================================================================

    def get_all_exam_sessions(self):
        return self.db.query(ExamSession, User.username).outerjoin(
            User, ExamSession.student_id == User.user_id
        ).filter(
            ExamSession.status == "COMPLETED"
        ).order_by(ExamSession.end_time.desc()).all()

    def override_score(self, session_id: int, new_score: float):
        """
        FR-17: Admin modifies the score. Report card and Exam are updated.
        """
        sess = self.db.query(ExamSession).filter(ExamSession.session_id == session_id).first()
        
        if sess:
            print(f"🔄 Admin Updating Score: ID {session_id} -> {new_score}")

            # 1. Update Exam Session
            sess.overall_score = new_score
            new_level = "A1"
            if new_score >= 85: new_level = "C1"
            elif new_score >= 70: new_level = "B2"
            elif new_score >= 50: new_level = "B1"
            elif new_score >= 30: new_level = "A2"
            
            sess.detected_level = new_level

            # 2. Update Report Card (LevelRecord)
            record = self.db.query(LevelRecord).filter(LevelRecord.student_id == sess.student_id).first()
            if record and sess.answers:
                first_q = sess.answers[0].question
                skill_type = first_q.skill_category.upper() if first_q else "GENERAL"

                if "READING" in skill_type: record.reading_level = new_level
                elif "WRITING" in skill_type: record.writing_level = new_level
                elif "LISTENING" in skill_type: record.listening_level = new_level
                elif "SPEAKING" in skill_type: record.speaking_level = new_level
                
                self._recalculate_overall_level(record)

            # 4. Save
            try:
                self.db.commit()
                self.db.refresh(sess)
                return True
            except Exception as e:
                self.db.rollback()
                return False
        
        return False

    def _recalculate_overall_level(self, record):
        level_map = { "A1": 20, "A2": 40, "B1": 60, "B2": 80, "C1": 100, "C2": 100 }
        
        r = level_map.get(record.reading_level, 20)
        w = level_map.get(record.writing_level, 20)
        l = level_map.get(record.listening_level, 20)
        s = level_map.get(record.speaking_level, 20)

        avg = (r + w + l + s) / 4

        final_level = "A1"
        if avg >= 85: final_level = "C1"
        elif avg >= 70: final_level = "B2"
        elif avg >= 50: final_level = "B1"
        elif avg >= 30: final_level = "A2"

        record.overall_level = final_level

    # =========================================================================
    # 4. TECHNICAL SUPPORT AND REPORTS (FR-20 ADDED)
    # =========================================================================

    def get_all_reports(self):
        """Lists all technical issue reports."""
        # Joining with User table to get the student name
        return self.db.query(ErrorReport, User.username).join(
            User, ErrorReport.student_id == User.user_id
        ).order_by(ErrorReport.created_at.desc()).all()

    def resolve_report(self, report_id: int):
        """Marks the issue as resolved (Deletes from database)."""
        report = self.db.query(ErrorReport).filter(ErrorReport.report_id == report_id).first()
        if report:
            try:
                self.db.delete(report)
                self.db.commit()
                return True
            except Exception as e:
                print(f"❌ Report Deletion Error: {e}")
                self.db.rollback()
                return False
        return False