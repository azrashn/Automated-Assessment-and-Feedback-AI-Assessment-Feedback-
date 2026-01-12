import os
import textstat
from datetime import datetime

# --- IMPORT GÜVENLİĞİ ---
# Kütüphaneler yüklü değilse uygulama çökmez, sadece o özellik çalışmaz.
try:
    import whisper
except ImportError:
    whisper = None
    print("⚠️ UYARI: 'whisper' modülü bulunamadı. Ses analizi devre dışı.")

try:
    import spacy
    # Modeli yüklemeyi dene
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("⚠️ UYARI: Spacy modeli (en_core_web_sm) bulunamadı. Dil analizi sınırlı olacak.")
        nlp = None
except ImportError:
    spacy = None
    nlp = None
    print("⚠️ UYARI: 'spacy' modülü bulunamadı.")

# --- FFmpeg AYARI (Mevcut ayarını koruyoruz) ---
# Eğer sisteminde farklı bir yoldaysa burası hata vermesin diye kontrol ekledik
ffmpeg_path = r"C:\ffmpeg\bin"
if os.path.exists(ffmpeg_path) and ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + ffmpeg_path

class AIModule:
    """
    Yapay Zeka İşlemleri Modülü.
    Veritabanından bağımsızdır (Stateless). Sadece veri alır ve işler.
    """
    def __init__(self):
        print("")

    def speech_to_text(self, audio_path: str) -> str:
        """Ses dosyasını metne çevirir."""
        if not self.stt_model:
            return ""
        if not os.path.exists(audio_path):
            return ""
        
        try:
            # fp16=False CPU uyumluluğu için
            result = self.stt_model.transcribe(audio_path, fp16=False)
            return result["text"].strip()
        except Exception as e:
            print(f"❌ Ses Analiz Hatası: {e}")
            return ""
        

    def analyze_writing(self, text, required_keywords=None):
        return {"score": 0, "feedback": "AI devre dışı"}

    def analyze_skill(self, skill_type, data, keywords=None):
        return 0.0

    def calculate_overall_score(self, scores):
        return 0.0

    def generate_feedback(self, scores):
        return ""
