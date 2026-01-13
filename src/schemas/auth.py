from pydantic import BaseModel, EmailStr
from typing import Optional

# Kayıt olurken gelen veri
class UserCreate(BaseModel):
    fullname: str  # HTML formundaki 'fullname' ile eşleşmeli
    email: EmailStr
    password: str
    student_number: Optional[str] = None

# Giriş yaparken gelen veri
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Kullanıcıya geri dönen veri (Şifreyi gizliyoruz)
class UserOut(BaseModel):
    user_id: int
    username: str
    role: str
    
    class Config:
        from_attributes = True # ORM nesnesini Pydantic modeline çevirir