from sqlalchemy.orm import Session
from src.repositories.policy_repo import PolicyRepository
from src.models.security import SecurityLog
import os

class SecurityService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PolicyRepository(db)

    def fetch_active_rules(self):

        active_policies = []
        exam_file_path = "src/templates/exam.html"

        try:
            if os.path.exists(exam_file_path):
                with open(exam_file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    
                    # Dosyadaki aktif (yorum olmayan) kodları tek bir metin yap
                    active_code = ""
                    for line in lines:
                        stripped = line.strip()
                        # Eğer satır boşsa veya // ile başlıyorsa (yorumsa) atla
                        if not stripped or stripped.startswith("//"):
                            continue
                        active_code += stripped + " "

                    # 1. Kural: Copy/Paste Kontrolü
                    if "copy" in active_code and "paste" in active_code and "preventDefault" in active_code:
                        active_policies.append("FR-19: Copy/Paste Protection (Clipboard Monitor)")

                    # 2. Kural: Sağ Tık (Context Menu) Kontrolü
                    if "contextmenu" in active_code and "preventDefault" in active_code:
                        active_policies.append("FR-19: Right-Click Context Menu Restriction")

            else:
                return ["HATA: exam.html dosyası bulunamadı!"]

        except Exception as e:
            print(f"Dosya okuma hatası: {e}")
            return ["Security check failed."]

        if not active_policies:
            return ["No active rules detected directly in Exam Module."]
            
        return active_policies

    def log_threat(self, details: str):
        log = SecurityLog(details=details)
        self.repo.insert_log_record(log)