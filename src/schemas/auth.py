from pydantic import BaseModel, EmailStr
from typing import Optional

# 1. Kayıt olurken gelen veri
class UserCreate(BaseModel):
    username: str  # DB ile uyumlu olması için 'username' kullanıyoruz
    email: EmailStr
    password: str
    student_number: Optional[str] = None

# 2. Giriş yaparken gelen veri
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 3. Kullanıcıya geri dönen veri (Şifreyi gizlemek için)
class UserOut(BaseModel):
    user_id: int
    username: str
    role: str
    
    class Config:
        from_attributes = True # ORM nesnesini Pydantic modeline çevirir

# 4. FR-2: PROFİL GÜNCELLEME İÇİN (YENİ)
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None