class UserRepository:
    def __init__(self, db):
        self.db = db

    def create_student(self, user_data, hashed_password, student_number):
        pass

    def check_email(self, email):
        return False

    def find_user_by_email(self, email):
        return None

    def find_user_by_id(self, uid):
        return None
