from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi import HTTPException, UploadFile
import os, shutil
from datetime import datetime

from src.repositories.exam_repo import ExamRepository
from src.services.ai_service import AIModule

# Sınav Süresi (Dakika)
DEFAULT_EXAM_DURATION = 20 

class ExamService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ExamRepository(db)
        self.ai = AIModule() # AI Modülünü Başlat

    def start_exam_session(self, user_id: int, skill: str, level: str):
        """
        Sınavı başlatır veya devam eden geçerli bir sınav varsa onu döndürür.
        """
        # 1. Döngü Kontrolü (Daha önce bu modülü bitirdi mi?)
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
                    detail=f"⚠️ {skill.upper()} You have already completed this module during this period."
                )

        # 2. Yarım Kalan Sınav Kontrolü
        active_session = self.repo.get_active_session(user_id)
        
        if active_session:
            # A) Süre dolmuş mu?
            if active_session.end_time and datetime.now() > active_session.end_time:
                self.repo.mark_session_expired(active_session)
            else:
                # B) Süre hala var -> Kaldığı yerden devam et
                questions = self.repo.get_questions_by_skill(skill, level)
                return active_session, questions

        # 3. Yeni Oturum Oluştur
        new_session = self.repo.create_session(
            student_id=user_id, 
            level=level,
            duration_minutes=DEFAULT_EXAM_DURATION
        )
        questions = self.repo.get_questions_by_skill(skill, level)

        return new_session, questions

    def save_answer(self, session_id: int, question_id: int, selected_option_id: int = None, text_response: str = None):
        """
        Cevabı kaydeder. ÖNCE SÜRE KONTROLÜ YAPAR.
        """
        session = self.repo.get_session(session_id)
        if not session:
            raise HTTPException(404, "Exam session not found.")
        
        # A) Statüs Kontrolü
        if session.status != "IN_PROGRESS":
            raise HTTPException(400, "This exam is completed or has expired.")

        # B) Süre Kontrolü
        if session.end_time and datetime.now() > session.end_time:
            self.repo.mark_session_expired(session)
            raise HTTPException(400, "Exam time is up! Your answer was not saved.")

        # C) Kayıt
        self.repo.save_answer(session_id, question_id, selected_option_id, text_response)

    def save_audio(self, file: UploadFile):
        os.makedirs("src/static/uploads", exist_ok=True)
        filename = f"rec_{datetime.now().timestamp()}.webm"
        file_path = f"src/static/uploads/{filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return f"/static/uploads/{filename}"

    def finalize_exam(self, session_id: int, skill_name: str = None):
        session = self.repo.get_session(session_id)
        if not session: raise HTTPException(404, "Session not found")
        
        scores = {}
        detected_speech_text = ""
        gemini_feedback_list = [] # Gemini'den gelen özel yorumları biriktirmek için

        #  A. SORULARI PUANLA 
        for ans in session.answers:
            q = ans.question
            score = 0.0
            is_answer_correct = False # Varsayılan yanlış

            if q.type == "MULTIPLE_CHOICE":
                correct_opt = next((o for o in q.options if o.is_correct), None)
                if correct_opt and ans.selected_option_id == correct_opt.option_id:
                    score = 100.0
                    is_answer_correct = True
    
            else:
                # Kullanıcı cevabını al (Text veya daha önce kaydedilmiş content)
                user_text = (ans.content or ans.text_response or "").strip()
                skill_cat = (q.skill_category or "WRITING").upper()

                #  SPEAKING: Önce Transkribe Etme
                if skill_cat == "SPEAKING":
                    audio_path = ans.content or ans.audio_path
                    if audio_path:
                        # Full path oluştur
                        full_path = f"src{audio_path}" if audio_path.startswith("/static") else audio_path
                        
                        # AI Servisini Çağır (Ses -> Metin)
                        transcribed_text = self.ai.speech_to_text(full_path)
                        
                        # Transkripti kaydet ki analizde görünsün
                        ans.content = transcribed_text 
                        user_text = transcribed_text
                        detected_speech_text = transcribed_text
                    else:
                        user_text = ""

                #  DEĞERLENDİRME (HİBRİT AI SİSTEMİ) 
                
                # A) KESİN CEVAP VARSA (Reading/Listening boşluk doldurma)
                correct_text_opt = next((o for o in q.options if o.is_correct), None)
                
                if correct_text_opt:
                    # String Normalizasyonu (Küçük harf, boşluk silme)
                    correct_text = correct_text_opt.content.strip().lower()
                    user_text_norm = user_text.strip().lower()
                    
                    if user_text_norm == correct_text:
                        score = 100.0
                        is_answer_correct = True
                    else:
                        score = 0.0
                
                # B) AI ANALİZİ (Essay / Speaking / Yorum Sorusu) - HİBRİT ÇAĞRI
                else:
                    if user_text:
                        # Gerekli verileri hazırla
                        topic = q.text if q.text else "General Task"
                        # Keywords listesini hazırla (Eski algoritma için şart!)
                        k_list = [k.strip() for k in q.keywords.split(",")] if q.keywords else []
                        
                        # session.difficulty kontrolü
                        exam_level = getattr(session, "difficulty", None) or getattr(session, "difficulty_level", "A1")
                        
                        # HİBRİT FONKSİYONU ÇAĞIR 
                        analysis = self.ai.evaluate_writing_hybrid(
                            text=user_text,
                            topic=topic,
                            level=exam_level,
                            keywords=k_list # Bu parametre eklendi!
                        )
                        
                        score = float(analysis.get("score", 0))
                        is_answer_correct = (score >= 60)
                        
                        # Gemini'den veya Sistemden gelen yorumu kaydet
                        if analysis.get("feedback_tr"):
                            gemini_feedback_list.append(analysis["feedback_tr"])
                            
                    else:
                        score = 0.0

            # SONUÇLARI KAYDET
            ans.is_correct = is_answer_correct # DB'ye yaz (Yeşil/Kırmızı rozet için)
            
            # Puanları kategoriye göre topla
            skill_key = q.skill_category or "General"
            if skill_key in scores:
                scores[skill_key] = (scores[skill_key] + score) / 2
            else:
                scores[skill_key] = score
                
        # Hiç cevap yoksa varsayılan puan
        if not scores and skill_name:
            scores[skill_name.upper()] = 0.0    
        
        # Genel Puan Hesaplama
        # Basit ortalama alıyoruz
        if scores:
            overall_score = round(sum(scores.values()) / len(scores), 1)
        else:
            overall_score = 0.0

        session.overall_score = overall_score
        session.status = "COMPLETED"
        session.end_time = datetime.now()
        
        # Seviye Belirle
        detected_level = "A1"
        if overall_score >= 85: detected_level = "C1"
        elif overall_score >= 70: detected_level = "B2"
        elif overall_score >= 50: detected_level = "B1"
        elif overall_score >= 30: detected_level = "A2"
        session.detected_level = detected_level 

        #   Level Record ve  feedback Güncelle 
        self._update_level_record(session.student_id, scores, detected_level)

        # Feedback Metni Oluşturma
        fb_text = ""
        if overall_score >= 85: fb_text = "🏆 Excellent! Your level is in the C1-C2 range."
        elif overall_score >= 70: fb_text = "✅ Very good. You're at B2 level."
        elif overall_score >= 50: fb_text = "📈 Average. You're at B1 level."
        else: fb_text = "⚠️ Needs improvement. You are at A1-A2 level."

        # Gemini Yorumlarını Ekle
        if gemini_feedback_list:
            fb_text += "\n\n🤖 AI / System Assessment:\n" + "\n".join(gemini_feedback_list)

        if detected_speech_text:
            fb_text += f"\n\n🗣️ Perceived Speech:\n\"{detected_speech_text}\""
        
        try:
            session.ai_feedback = fb_text
            # session.status = "COMPLETED" 
            self.db.commit()
            print(f"✅ Successfully recorded: Session {session_id}")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Database record error: {e}")

        return {
            "overall_score": overall_score,
            "feedback": fb_text,
            "breakdown": scores
        }

    def _update_level_record(self, student_id: int, scores: dict, detected_level: str):
        record = self.repo.get_level_record(student_id)
        if record:
            skill_type = list(scores.keys())[0].upper() if scores else "GENERAL"
            if "READING" in skill_type: record.reading_level = detected_level
            elif "WRITING" in skill_type: record.writing_level = detected_level
            elif "LISTENING" in skill_type: record.listening_level = detected_level
            elif "SPEAKING" in skill_type: record.speaking_level = detected_level
            self.update_student_overall_level(student_id)

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
        print(f"📊 New General Level: {final_level} (Average: {avg_score})")