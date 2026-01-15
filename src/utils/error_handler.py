from fastapi import HTTPException

def check_found(resource, name: str = "Kayıt"):
    """
    Veritabanından çekilen objenin varlığını kontrol eder.
    Yoksa 404 hatası fırlatır.
    
    Kullanım:
    user = db.query(User).get(user_id)
    check_found(user, "Kullanıcı")
    """
    if not resource:
        raise HTTPException(status_code=404, detail=f"{name} bulunamadı")

def raise_bad_request(message: str):
    """Genel 400 hatası fırlatır."""
    raise HTTPException(status_code=400, detail=message)

def raise_unauthorized(message: str = "Yetkisiz işlem"):
    """Genel 401 hatası fırlatır."""
    raise HTTPException(status_code=401, detail=message)