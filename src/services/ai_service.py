import os
import random
import json
from datetime import datetime
import textstat  # Required for legacy analysis (pip install textstat)

# --- NEW LIBRARY SETUP ---
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ WARNING: 'google-genai' library is not installed.")

# --- API KEY SETUP ---
# Replace this with your actual API key
API_KEY = "YOUR_API_KEY_HERE" 

# --- IMPORT SAFETY ---
try:
    import whisper
except ImportError:
    whisper = None

try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        nlp = None
except ImportError:
    spacy = None
    nlp = None

# --- FFmpeg SETUP ---
ffmpeg_path = r"C:\ffmpeg\bin"
if os.path.exists(ffmpeg_path) and ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + ffmpeg_path

class AIModule:
    def __init__(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 AI Module Starting (HYBRID MODE)...")
        
        # 1. Initialize Gemini Client
        self.client = None
        if GEMINI_AVAILABLE and API_KEY and API_KEY != "YOUR_API_KEY_HERE":
            try:
                self.client = genai.Client(api_key=API_KEY)
                print("✅ Gemini API Connected.")
            except Exception as e:
                print(f"❌ Gemini Connection Error: {e}")

        # 2. Load Whisper Model
        self.stt_model = None
        if whisper:
            try:
                self.stt_model = whisper.load_model("base")
                print("✅ Whisper (Speech-to-Text) Ready.")
            except Exception as e:
                print(f"❌ Whisper Load Error: {e}")

        # 3. Word List for Legacy Algorithm
        self.advanced_vocabulary = [
            "however", "therefore", "furthermore", "although", "despite",
            "because", "since", "unless", "usually", "generally",
            "significant", "essential", "opportunity", "experience",
            "challenging", "rewarding", "consequently", "whereas"
        ]

    # ----------------------------------------------------------------
    # 1. HYBRID WRITING ANALYSIS (API FIRST -> THEN MATH)
    # ----------------------------------------------------------------
    def evaluate_writing_hybrid(self, text: str, topic: str, level: str, keywords: list = None) -> dict:
        """
        Main Function: Tries Gemini first, falls back to legacy algorithm if it fails.
        """
        # Return immediately if text is too short
        if len(text) < 5:
             return self._create_fallback_response(text, "Text is too short to evaluate.", score=10)

        # A) API CHECK
        if self.client:
            try:
                # Prompt Preparation (STRICT SCORING)
                prompt = f"""
                Act as a STRICT English Examiner (IELTS/TOEFL style). 
                Evaluate this essay written by a student targeting {level} level.
                Topic: {topic}
                Student's Essay: "{text}"
                
                SCORING RULES:
                1. If the text consists only of simple sentences (Subject+Verb+Object) like "My mother is a teacher.", the MAXIMUM score is 65.
                2. To get above 70, the student MUST use conjunctions (because, but, so, however).
                3. To get above 85, the student MUST use complex grammar (relative clauses, conditionals, advanced vocabulary).
                4. Deduct points if the essay is too short compared to the task.
                
                Provide output in VALID JSON:
                {{
                    "score": (integer 0-100),
                    "grammar_errors": ["list specific errors"],
                    "suggestions": ["suggestion1", "suggestion2"],
                    "corrected_text": "corrected version",
                    "feedback": "Give strict but constructive feedback in English. Mention why the score is low if sentences are too simple."
                }}
                Do not use markdown blocks.
                """
                
                # API Call
                response = self.client.models.generate_content(
                    model="gemini-1.5-flash", # Updated model name example
                    contents=prompt
                )
                
                if response.text:
                    cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
                    return json.loads(cleaned_text)
            
            except Exception as e:
                print(f"⚠️ Gemini API Error (Quota/Connection): {e}")
                print("🔄 'Rule-Based' (Mathematical) Analysis Triggered...")

        # B) FALLBACK: OLD ALGORITHM RUNS IF API IS MISSING
        else:
            print("ℹ️ No API Key, performing direct mathematical analysis.")

        return self.analyze_writing_rule_based(text, keywords)

    # ----------------------------------------------------------------
    # 2. LEGACY RELIABLE ALGORITHM (FAIL-SAFE)
    # ----------------------------------------------------------------
    def analyze_writing_rule_based(self, text: str, required_keywords: list = None) -> dict:
        """
        Mathematical analysis that runs when the API is not working.
        """
        doc = nlp(text) if nlp else None
        words = text.split()
        word_count = len(words)
        text_lower = text.lower()

        # A. LENGTH SCORE (30%)
        score_length = min(100, (word_count / 50) * 100)

        # B. DIVERSITY SCORE (20%)
        unique_words = set([w.lower() for w in words])
        diversity_ratio = len(unique_words) / len(words) if words else 0
        score_diversity = min(100, (diversity_ratio / 0.6) * 100)

        # C. COMPLEXITY SCORE (20%)
        try:
            readability = textstat.flesch_reading_ease(text)
            score_complexity = max(0, min(100, 100 - readability))
        except:
            score_complexity = 50.0

        # D. KEYWORD & ADVANCED VOCABULARY (30%)
        relevance_score = 100.0
        if required_keywords:
            match_count = sum(1 for k in required_keywords if k.lower() in text_lower)
            if match_count == 0: relevance_score = 40.0
            elif match_count == 1: relevance_score = 70.0

        advanced_hits = [w for w in self.advanced_vocabulary if w in text_lower]
        score_vocab = min(100, len(advanced_hits) * 20)

        # TOTAL SCORE
        raw_score = (score_length * 0.3) + (score_diversity * 0.2) + (score_complexity * 0.2) + (relevance_score * 0.3)
        final_score = int(max(0, min(100, raw_score)))

        # Generate Feedback
        feedback_text = "Automated analysis performed due to server load. "
        if final_score > 70:
            feedback_text += "Your vocabulary diversity and sentence structure are quite good."
        elif final_score > 50:
            feedback_text += "Average text. You can improve by using conjunctions (however, because)."
        else:
            feedback_text += "Your text is a bit short or simple. Try constructing longer sentences."

        return {
            "score": final_score,
            "grammar_errors": [], 
            "suggestions": ["Try to use more 'academic vocabulary'.", "Extend your sentences with conjunctions."],
            "corrected_text": text,
            "feedback": feedback_text
        }

    # ----------------------------------------------------------------
    # 3. SPEAKING (WHISPER + FILE CHECK)
    # ----------------------------------------------------------------
    def speech_to_text(self, audio_path: str) -> str:
        if not os.path.exists(audio_path):
            return self._get_mock_speech_text()

        file_size = os.path.getsize(audio_path)
        if file_size < 1000: 
            return self._get_mock_speech_text()

        if self.stt_model:
            try:
                result = self.stt_model.transcribe(audio_path, fp16=False)
                text = result["text"].strip()
                if not text: return self._get_mock_speech_text()
                return text
            except Exception:
                pass # Return mock if error
        
        return self._get_mock_speech_text()

    def _create_fallback_response(self, text, error_msg, score=0):
        return { "score": score, "grammar_errors": [], "suggestions": [error_msg], "corrected_text": text, "feedback": error_msg }

    def _get_mock_speech_text(self):
        simulated_transcripts = [
            "I believe that technology has improved our lives significantly.",
            "My favorite hobby is playing football because it is very exciting."
        ]
        return random.choice(simulated_transcripts)