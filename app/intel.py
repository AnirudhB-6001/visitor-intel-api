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

# 🔎 Extract specific field from entropy_data (supports multiple aliases)
def extract_entropy_field(entropy: dict, key: str):
    field_map = {
        "user_agent": ["userAgent"],
        "screen_res": ["screen"],
        "color_depth": ["colorDepth"],
        "timezone": ["timezone"],
        "language": ["language"],
        "platform": ["platform"],
        "device_memory": ["deviceMemory"],
        "cpu_cores": ["hardwareConcurrency"],
        "gpu_vendor": ["webglVendor"],
        "gpu_renderer": ["webglRenderer"],
        "canvas_hash": ["canvas"],
        "audio_hash": ["audio"]
    }
    aliases = field_map.get(key, [])
    for alias in aliases:
        if alias in entropy:
            return entropy[alias]
    return None

# 🧠 Compute and return the most probable alias based on entropy similarity
def get_probable_alias(db: Session, entropy_data: dict, current_fingerprint: str = None) -> str | None:
    candidates = (
        db.query(VisitorLog)
        .filter(VisitorLog.entropy_data.isnot(None))
        .filter(VisitorLog.fingerprint_id != current_fingerprint)
        .all()
    )

    if not candidates:
        return None

    def score_match(past: VisitorLog) -> float:
        match_score = 0.0
        total_weight = 0.0
        for key, weight in WEIGHTS.items():
            current_value = extract_entropy_field(entropy_data, key)
            past_value = extract_entropy_field(past.entropy_data or {}, key)
            if current_value is not None and past_value is not None and current_value == past_value:
                match_score += weight
            total_weight += weight
        return match_score / total_weight if total_weight > 0 else 0.0

    ranked = sorted(
        [(p.visitor_alias, score_match(p)) for p in candidates if p.visitor_alias],
        key=lambda x: x[1],
        reverse=True,
    )

    if ranked and ranked[0][1] >= THRESHOLD:
        print(f"🧠 Probable alias match: {ranked[0][0]} (Score: {ranked[0][1]:.2f})")
        return ranked[0][0]

    return None
