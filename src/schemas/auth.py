from pydantic import BaseModel

# Kayıt olurken gelen veri
class UserCreate(BaseModel):
    pass

# Giriş yaparken gelen veri
class UserLogin(BaseModel):
    pass

# Kullanıcıya geri dönen veri (Şifreyi gizliyoruz)
class UserOut(BaseModel):
    pass