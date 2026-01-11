from src.database import Base

class User(Base):
    __tablename__ = "users"
pass    

class Student(User):
    __tablename__ = "students"
pass    

class Administrator(User):
    __tablename__ = "administrators"
pass 

class LevelRecord(Base):
    __tablename__ = "level_records"
pass