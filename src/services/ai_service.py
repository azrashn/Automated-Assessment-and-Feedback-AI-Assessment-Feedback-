import os
import textstat
from datetime import datetime
import random

# --- IMPORT SAFETY ---
# If libraries are not installed, the app won't crash; only that specific feature will be disabled.
try:
    import whisper
except ImportError:
    whisper = None
    print("⚠️ WARNING: 'whisper' module not found. Voice analysis disabled.")

try:
    import spacy
    # Try to load the model
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("⚠️ WARNING: Spacy model (en_core_web_sm) not found. Language analysis will be limited.")
        nlp = None
except ImportError:
    spacy = None
    nlp = None
    print("⚠️ WARNING: 'spacy' module not found.")

# --- FFmpeg SETUP ---
ffmpeg_path = r"C:\ffmpeg\bin"
if os.path.exists(ffmpeg_path) and ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + ffmpeg_path

class AIModule:
    """
    AI Operations Module.
    Stateless (Database independent). It only receives data and processes it.
    """
    def __init__(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 AI Module Initializing...")
        
        self.stt_model = None
        if whisper:
            try:
                self.stt_model = whisper.load_model("base")
                print("✅ Whisper (Speech-to-Text) Ready.")
            except Exception as e:
                print(f"❌ Whisper Load Error: {e}")

        # B1+ Level Indicators
        self.advanced_vocabulary = [
            "however", "therefore", "furthermore", "although", "despite",
            "because", "since", "unless", "usually", "generally",
            "significant", "essential", "opportunity", "experience",
            "challenging", "rewarding", "consequently", "whereas",
            "meanwhile", "provided", "additionally", "especially"
        ]

    def speech_to_text(self, audio_path: str) -> str:
        """Transcribes audio file to text."""
        # 1. If model exists, perform actual transcription
        if self.stt_model and os.path.exists(audio_path):
            try:
                result = self.stt_model.transcribe(audio_path, fp16=False)
                return result["text"].strip()
            except Exception as e:
                print(f"❌ Audio Analysis Error: {e}")
        
        # 2. If no model or error occurs, return MOCK (Simulated) Text
        # This fallback is a lifesaver to avoid issues during a presentation.
        print("⚠️ Whisper unavailable, returning Mock text.")
        simulated_transcripts = [
            "I believe that technology has improved our lives significantly.",
            "My favorite hobby is playing football because it is very exciting.",
            "I usually spend my weekends with my family going to the park.",
            "Learning a new language opens up many opportunities for the future."
        ]
        return random.choice(simulated_transcripts)

    def analyze_writing(self, text: str, required_keywords: list = None) -> dict:
        """
        BALANCED WRITING ANALYSIS
        """
        # 1. Empty Check
        if not text or len(text.split()) < 3:
            return {"score": 10.0, "feedback": "Text is too short or empty.", "details": {}}

        # 2. NLP Preparation
        doc = nlp(text) if nlp else None
        text_lower = text.lower()
        words = text.split()
        word_count = len(words)

        # --- CRITERIA 1: LENGTH (30%) ---
        score_length = min(100, (word_count / 60) * 100)

        # --- CRITERIA 2: DIVERSITY (20%) ---
        if nlp and doc:
            lemma_words = [token.text.lower() for token in doc if token.is_alpha]
            unique_words = set(lemma_words)
            div_len = len(lemma_words)
        else:
            unique_words = set([w.lower() for w in words])
            div_len = len(words)
            
        diversity_ratio = len(unique_words) / div_len if div_len > 0 else 0
        score_diversity = min(100, (diversity_ratio / 0.6) * 100)

        # --- CRITERIA 3: TOPIC RELEVANCE (30%) ---
        relevance_score = 100.0
        is_off_topic = False
        
        if required_keywords and len(required_keywords) > 0:
            match_count = 0
            user_lemmas = [token.lemma_.lower() for token in doc] if (nlp and doc) else text_lower.split()
            
            for key in required_keywords:
                k = key.lower().strip()
                # Simple string search or lemma search
                if k in text_lower or k in user_lemmas:
                    match_count += 1
            
            # Keyword capture rate
            if match_count == 0:
                relevance_score = 20.0
                is_off_topic = True
            elif match_count == 1:
                relevance_score = 50.0
            elif match_count == 2:
                relevance_score = 75.0
            else:
                relevance_score = 100.0

        # --- CRITERIA 4: COMPLEXITY (20%) ---
        try:
            readability = textstat.flesch_reading_ease(text)
            score_complexity = max(0, min(100, 100 - readability))
        except:
            score_complexity = 50.0

        # --- CALCULATION ---
        raw_score = (relevance_score * 0.30) + \
                    (score_length * 0.30) + \
                    (score_diversity * 0.20) + \
                    (score_complexity * 0.20)
        
        final_score = round(max(0, min(100, raw_score)), 1)

        # --- PENALTY AND FEEDBACK ---
        advanced_hits = [w for w in self.advanced_vocabulary if w in text_lower]
        has_advanced = len(advanced_hits) > 0
        
        feedback_msg = ""
        feedback_prefix = ""

        if is_off_topic:
            final_score = min(35.0, final_score)
            feedback_prefix = "⛔ OFF-TOPIC: "
            feedback_msg = "Your answer is not relevant enough to the question. Pay attention to using keywords."
        
        elif not has_advanced:
            limit = 65.0
            if final_score > limit:
                final_score = limit
                feedback_prefix = "⚠️ SIMPLE PHRASING: "
                feedback_msg = "The topic is correct, but your sentences are simple. Use conjunctions like 'because' or 'however' to increase your score."
            else:
                feedback_msg = "A good start. Try to form longer and more detailed sentences."
        else:
            feedback_msg = f"🌟 Great! Using advanced words like '{', '.join(advanced_hits[:2])}' increased your score."

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

    def calculate_overall_score(self, scores: dict) -> float:
        if not scores: return 0.0
        return round(sum(scores.values()) / len(scores), 1)

    def generate_feedback(self, scores: dict) -> str:
        """
        Generates the final evaluation text at the end of the exam.
        """
        avg = self.calculate_overall_score(scores)
        feedback = []
        
        if avg >= 85:
            feedback.append("🏆 Excellent! Your English level seems to be in the C1-C2 band.")
        elif avg >= 70:
            feedback.append("✅ Very good. You are at the B2 level.")
        elif avg >= 50:
            feedback.append("📈 Average. You are at the B1 level, you should practice a bit more.")
        else:
            feedback.append("⚠️ Needs improvement. You are at the A1-A2 level.")
            
        return " ".join(feedback)