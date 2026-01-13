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
        

   def analyze_writing(self, text: str, required_keywords: list = None) -> dict:
        """
        DENGELİ WRITING ANALİZİ (Mevcut Mantık Korundu)
        """
        # 1. Boş Kontrolü
        if not text or len(text.split()) < 3:
            return {"score": 10.0, "feedback": "Metin çok kısa veya boş.", "details": {}}

        # 2. NLP Hazırlık
        doc = nlp(text) if nlp else None
        text_lower = text.lower()
        words = text.split()
        word_count = len(words)

        # --- KRİTER 1: UZUNLUK (%30) ---
        score_length = min(100, (word_count / 60) * 100)

        # --- KRİTER 2: ÇEŞİTLİLİK (%20) ---
        if nlp and doc:
            lemma_words = [token.text.lower() for token in doc if token.is_alpha]
            unique_words = set(lemma_words)
            div_len = len(lemma_words)
        else:
            unique_words = set([w.lower() for w in words])
            div_len = len(words)
            
        diversity_ratio = len(unique_words) / div_len if div_len > 0 else 0
        score_diversity = min(100, (diversity_ratio / 0.6) * 100)

        # --- KRİTER 3: KONU UYGUNLUĞU (%30) ---
        relevance_score = 100.0
        is_off_topic = False
        
        if required_keywords and len(required_keywords) > 0:
            match_count = 0
            # Lemma desteği varsa kullan, yoksa düz string araması
            user_lemmas = [token.lemma_.lower() for token in doc] if (nlp and doc) else text_lower.split()
            
            for key in required_keywords:
                k = key.lower()
                if k in text_lower or k in user_lemmas:
                    match_count += 1
            
            # Senin kuralların:
            if match_count <= 1:
                relevance_score = 0.0
                is_off_topic = True
            elif match_count == 2:
                relevance_score = 60.0
            elif match_count == 3:
                relevance_score = 80.0
            else:
                relevance_score = 100.0

        # --- KRİTER 4: KARMAŞIKLIK (%20) ---
        try:
            readability = textstat.flesch_reading_ease(text)
            score_complexity = max(0, min(100, 100 - readability))
        except:
            score_complexity = 50.0

        # --- HESAPLAMA ---
        raw_score = (relevance_score * 0.30) + \
                    (score_length * 0.30) + \
                    (score_diversity * 0.20) + \
                    (score_complexity * 0.20)
        
        final_score = round(max(0, min(100, raw_score)), 1)

        # --- CEZA VE FEEDBACK ---
        advanced_hits = [w for w in self.advanced_vocabulary if w in text_lower]
        has_advanced = len(advanced_hits) > 0
        
        feedback_msg = ""
        feedback_prefix = ""

        if is_off_topic:
            final_score = min(35.0, final_score)
            feedback_prefix = "⛔ KONU DIŞI: "
            feedback_msg = "Cevabınız soruyla yeterince ilgili değil. Anahtar kelimeleri kullanmaya özen gösterin."
        
        elif not has_advanced:
            limit = 65.0
            if final_score > limit:
                final_score = limit
                feedback_prefix = "⚠️ BASİT ANLATIM: "
                feedback_msg = "Konu doğru ancak cümleleriniz basit. Puanınızı artırmak için 'because', 'however' gibi bağlaçlar kullanın."
            else:
                feedback_msg = "Güzel bir başlangıç. Daha uzun ve detaylı cümleler kurmayı dene."
        else:
            feedback_msg = f"🌟 Harika! '{', '.join(advanced_hits[:2])}' gibi gelişmiş kelimeler kullanman puanını artırdı."

        return {
            "score": final_score,
            "feedback": f"{feedback_prefix}{feedback_msg}",
            "breakdown": {
                "length": score_length,
                "relevance": relevance_score,
                "diversity": score_diversity,
                "complexity": score_complexity
            }
        }
def analyze_skill(self, skill_type, data, keywords=None):
        return 0.0
        
def calculate_overall_score(self, scores):
        return 0.0
        
        
        
        
        
def generate_feedback(self, scores):
        return ""
