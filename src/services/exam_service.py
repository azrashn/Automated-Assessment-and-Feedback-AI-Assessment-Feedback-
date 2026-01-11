class ExamService:
    def __init__(self, db):
        self.db = db
        # self.ai = AIModule() ile daha sonra mantığı eklenecek

    def update_student_overall_level(self, student_id):
        pass

    def save_audio(self, file):
        return "dosya_yolu"

    def start_exam_session(self, user_id, skill, level):
        # Dönüş değeri session ve questions olmalı
        return None, []

    def save_answer(self, session_id, question_id, selected_option_id, text_response):
        pass

    def finalize_exam(self, session_id):
        return {}
    
    def determine_next_module(self, student_id: int, current_skill: str):
        pass

    def get_exam_duration(self, session_id: int):
        pass