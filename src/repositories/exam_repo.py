class ExamRepository:
    def __init__(self, db):
        self.db = db

    def create_session(self, student_id):
        pass

    def get_session(self, sid):
        return None

    def find_records_by_student_id(self, student_id):
        return []

    def save_answer(self, answer):
        pass

    def get_answer_by_session_question(self, session_id, question_id):
        return None

    def save_final_result(self, session, report):
        pass
