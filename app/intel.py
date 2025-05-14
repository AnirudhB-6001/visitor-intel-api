# app/intel.py

from sqlalchemy.orm import Session
from app.models import VisitorLog
from difflib import SequenceMatcher

# ⚙️ You can adjust these weights to tune matching behavior
WEIGHTS = {
    "user_agent": 2.0,
    "screen_res": 1.5,
    "color_depth": 1.0,
    "timezone": 1.0,
    "language": 1.0,
    "platform": 1.5,
    "device_memory": 1.0,
    "cpu_cores": 1.0,
    "gpu_vendor": 2.0,
    "gpu_renderer": 2.0,
    "canvas_hash": 2.0,
    "audio_hash": 2.0,
}

THRESHOLD = 0.8  # Match confidence threshold

# 🔍 Fuzzy matching between two values (default to 0 if either is None)
def fuzzy_match(val1, val2):
    if not val1 or not val2:
        return 0.0
    return SequenceMatcher(None, str(val1), str(val2)).ratio()

def get_probable_alias(current_entropy: dict, db: Session) -> str | None:
    candidates = db.query(VisitorLog).filter(VisitorLog.entropy_data.isnot(None)).all()
    best_match = None
    best_score = 0.0

    for row in candidates:
        entropy = row.entropy_data or {}
        score = 0.0
        weight_sum = 0.0

        for key, weight in WEIGHTS.items():
            sim = fuzzy_match(current_entropy.get(key), entropy.get(key))
            score += sim * weight
            weight_sum += weight

        final_score = score / weight_sum if weight_sum else 0.0

        if final_score > best_score:
            best_score = final_score
            best_match = row.visitor_alias

    if best_score >= THRESHOLD:
        return best_match
    return None
