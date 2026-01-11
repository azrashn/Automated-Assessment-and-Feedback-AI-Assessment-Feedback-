from pydantic import BaseModel

class OptionOut(BaseModel):
    class Config:
        from_attributes = True

class QuestionOut(BaseModel):
    class Config:
        from_attributes = True

class AnswerCreate(BaseModel):
    pass

class ExamSubmit(BaseModel):
    pass

class OptionCreate(BaseModel):
    pass

class QuestionCreate(BaseModel):
    pass

class ScoreOverride(BaseModel):
    pass
