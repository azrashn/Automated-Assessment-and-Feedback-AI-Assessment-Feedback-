class AIModule:
    def __init__(self):
        print("")

    def speech_to_text(self, audio_path):
        return ""

    def analyze_writing(self, text, required_keywords=None):
        return {"score": 0, "feedback": "AI devre dışı"}

    def analyze_skill(self, skill_type, data, keywords=None):
        return 0.0

    def calculate_overall_score(self, scores):
        return 0.0

    def generate_feedback(self, scores):
        return ""
