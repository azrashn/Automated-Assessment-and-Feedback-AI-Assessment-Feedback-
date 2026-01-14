from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi import HTTPException, UploadFile
from datetime import datetime
import os, shutil

DEFAULT_EXAM_DURATION = 1

class ExamService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ExamRepository(db)
        self.ai = AIModule()

    def update_student_overall_level(self, student_id):
        pass

    def save_audio(self, file):
        return "dosya_yolu"

    def start_exam_session(self, user_id: int, skill: str, level: str):
        """
        Sınavı başlatır veya devam eden geçerli bir sınav varsa onu döndürür.
        """
        # 1. Döngü Kontrolü (Business Logic)
        record = self.repo.get_level_record(user_id)
        if record:
            completed_skills = []
            if record.reading_level: completed_skills.append("READING")
            if record.writing_level: completed_skills.append("WRITING")
            if record.listening_level: completed_skills.append("LISTENING")
            if record.speaking_level: completed_skills.append("SPEAKING")

            if len(completed_skills) == 4:
                self.repo.reset_level_record(record)
            elif skill.upper() in completed_skills:
                raise HTTPException(
                    status_code=400, 
                    detail=f"⚠️ {skill.upper()} modülünü bu dönemde zaten tamamladınız."
                )

        # 2. Yarım Kalan Sınav Kontrolü
        active_session = self.repo.get_active_session(user_id)
        
        if active_session:
            # Süre dolmuş mu?
            if active_session.end_time and datetime.now() > active_session.end_time:
                self.repo.mark_session_expired(active_session)
            else:
                # Süre hala var -> Mevcut Oturumu Döndür (Resume)
                questions = self.repo.get_questions_by_skill(skill, level)
                return active_session, questions

        # 3. Yeni Oturum (Süre Tanımlı)
        new_session = self.repo.create_session(
            student_id=user_id, 
            level=level,
            duration_minutes=DEFAULT_EXAM_DURATION
        )
        questions = self.repo.get_questions_by_skill(skill, level)

        return new_session, questions


    def save_answer(self, session_id: int, question_id: int, selected_option_id: int = None, text_response: str = None):
        """
        Cevabı kaydeder. Önce Süre Kontrolü Yapar.
        """
        session = self.repo.get_session(session_id)
        if not session:
            raise HTTPException(404, "Sınav oturumu bulunamadı.")
        
        # Statüs Kontrolü
        if session.status != "IN_PROGRESS":
            raise HTTPException(400, "Bu sınav tamamlanmış veya süresi dolmuş.")

        # Süre Kontrolü 
        if session.end_time and datetime.now() > session.end_time:
            self.repo.mark_session_expired(session)
            raise HTTPException(400, "Sınav süresi doldu! Cevabınız kaydedilmedi.")

        # Kayıt
        self.repo.save_answer(session_id, question_id, selected_option_id, text_response)

    def finalize_exam(self, session_id):
        return {}
    
    def determine_next_module(self, student_id: int, current_skill: str):
        pass

    def get_exam_duration(self, session_id: int):
        pass