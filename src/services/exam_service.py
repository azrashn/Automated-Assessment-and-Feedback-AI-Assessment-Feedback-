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
        
        
    def update_student_overall_level(self, student_id: int):
        record = self.repo.get_level_record(student_id)
        if not record: return 

        level_points = { "A1": 20, "A2": 40, "B1": 60, "B2": 80, "C1": 100, "C2": 100 }
        r_p = level_points.get(record.reading_level, 20)
        w_p = level_points.get(record.writing_level, 20)
        l_p = level_points.get(record.listening_level, 20)
        s_p = level_points.get(record.speaking_level, 20)

        total_score = r_p + w_p + l_p + s_p
        avg_score = total_score / 4

        final_level = "A1"
        if avg_score >= 85: final_level = "C1"
        elif avg_score >= 70: final_level = "B2"
        elif avg_score >= 50: final_level = "B1"
        elif avg_score >= 30: final_level = "A2"

        record.overall_level = final_level
        print(f"📊 Yeni Genel Seviye: {final_level} (Ortalama: {avg_score})")
def save_audio(self, file: UploadFile):
        os.makedirs("src/static/uploads", exist_ok=True)
        filename = f"rec_{datetime.now().timestamp()}.webm"
        file_path = f"src/static/uploads/{filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return f"/static/uploads/{filename}" 
        
        
        
        
        
        
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

def finalize_exam(self, session_id: int, skill_name: str = None):
        session = self.repo.get_session(session_id)
        if not session: raise HTTPException(404, "Session not found")
        
        # Finalize ederken de süre kontrolü yapalım
        if session.status == "EXPIRED":
            raise HTTPException(400, "Sınav süresi dolduğu için sonuçlandırılamadı.")
        
        scores = {}
        detected_speech_text = ""

        # --- A. Soruları Puanla ---
        for ans in session.answers:
            q = ans.question
            score = 0.0
            
            if q.type == "MULTIPLE_CHOICE":
                correct_opt = next((o for o in q.options if o.is_correct), None)
                if correct_opt and ans.selected_option_id == correct_opt.option_id:
                    score = 100.0
            else:
                # AI Analizi
                skill_cat = (q.skill_category or "WRITING").upper()
                keywords = q.keywords

                if skill_cat == "SPEAKING":
                    audio_path = ans.content or ans.audio_path
                    if audio_path:
                        full_path = f"src{audio_path}" if audio_path.startswith("/static") else audio_path
                        transcribed_text = self.ai.speech_to_text(full_path)
                        ans.content = transcribed_text 
                        detected_speech_text = transcribed_text

                        if transcribed_text:
                            k_list = [k.strip() for k in keywords.split(",")] if keywords else []
                            analysis = self.ai.analyze_writing(transcribed_text, required_keywords=k_list)
                            bonus = 1.15 if "⛔" not in analysis["feedback"] else 1.0
                            score = min(100, analysis["score"] * bonus)
                        else:
                            score = 0.0
                    else:
                        score = 0.0
                else:
                    data = ans.content or ""
                    k_list = [k.strip() for k in keywords.split(",")] if keywords else []
                    result = self.ai.analyze_writing(data, required_keywords=k_list)
                    score = result["score"]
            
            skill_key = q.skill_category or "General"
            if skill_key in scores:
                scores[skill_key] = (scores[skill_key] + score) / 2
            else:
                scores[skill_key] = score
                
            # Eğer hiç cevap yoksa (scores boşsa), dışarıdan gelen skill ismini kullan
        if not scores and skill_name:
            scores[skill_name.upper()] = 0.0    
        
        # --- B. Sonuçları Hesapla ---
        overall_score = self.ai.calculate_overall_score(scores)
        session.overall_score = overall_score
        session.status = "COMPLETED"
        session.end_time = datetime.now() # Gerçek bitiş zamanı
        
        detected_level = "A1"
        if overall_score >= 85: detected_level = "C1"
        elif overall_score >= 70: detected_level = "B2"
        elif overall_score >= 50: detected_level = "B1"
        elif overall_score >= 30: detected_level = "A2"
        session.detected_level = detected_level 

        # --- C. Karne Güncelle ---
        self._update_level_record(session.student_id, scores, detected_level)

        # --- D. Feedback ---
        fb_text = self.ai.generate_feedback(scores)
        if detected_speech_text:
            fb_text += f"\n\n🗣️ Algılanan Konuşma:\n\"{detected_speech_text}\""
        
        self.repo.commit()
        
        return {
            "overall_score": overall_score,
            "feedback": fb_text,
            "breakdown": scores
        } 
        
        
def determine_next_module(self, student_id: int, current_skill: str):
        pass 




def get_exam_duration(self, session_id: int):
        pass