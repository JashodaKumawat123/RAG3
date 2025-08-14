# from typing import Dict, List, Tuple
# from math import exp
# import sqlite3

# from .user import DB_PATH

# # Mastery and prediction utilities

# def _sigmoid(x: float) -> float:
# 	return 1.0 / (1.0 + exp(-x))


# def load_progress(user_id: str) -> List[Tuple[str, float]]:
# 	conn = sqlite3.connect(DB_PATH)
# 	cursor = conn.cursor()
# 	cursor.execute("SELECT topic, score FROM progress WHERE user_id = ?", (user_id,))
# 	rows = cursor.fetchall()
# 	conn.close()
# 	return [(r[0], float(r[1])) for r in rows]


# def load_interactions(user_id: str) -> List[Tuple[str, float, float, float]]:
# 	"""Returns (competency, score, difficulty, time_spent). If the table is missing, returns empty list."""
# 	conn = sqlite3.connect(DB_PATH)
# 	cursor = conn.cursor()
# 	try:
# 		cursor.execute("SELECT competency, score, difficulty, time_spent FROM interactions WHERE user_id = ?", (user_id,))
# 		rows = cursor.fetchall()
# 		return [(r[0], float(r[1] or 0.0), float(r[2] or 0.5), float(r[3] or 0.0)) for r in rows]
# 	except Exception:
# 		return []
# 	finally:
# 		conn.close()


# def estimate_mastery(user_id: str) -> Dict[str, float]:
# 	"""Compute mastery per competency using an exponentially-weighted average of scores from progress and interactions."""
# 	alpha = 0.6  # weight for recent events
# 	mastery: Dict[str, float] = {}
# 	counts: Dict[str, float] = {}

# 	for topic, score in load_progress(user_id):
# 		mastery[topic] = mastery.get(topic, 0.0) * (1 - alpha) + score * alpha
# 		counts[topic] = counts.get(topic, 0.0) + 1

# 	for comp, score, difficulty, time_spent in load_interactions(user_id):
# 		adj = max(0.0, min(1.0, score - (difficulty - 0.5) * 0.2))
# 		mastery[comp] = mastery.get(comp, 0.0) * (1 - alpha) + adj * alpha
# 		counts[comp] = counts.get(comp, 0.0) + 1

# 	# Default unknown competencies to mid-level mastery
# 	for comp in ["arrays","linked-lists","stacks","queues","trees","graphs","dp"]:
# 		if comp not in mastery:
# 			mastery[comp] = 0.5
# 	return mastery


# def predict_performance(user_id: str, competency: str, difficulty: float = 0.5) -> float:
# 	"""Predict probability of success based on mastery and task difficulty (0..1)."""
# 	m = estimate_mastery(user_id).get(competency, 0.5)
# 	# Simple logistic: logit = a*(m - difficulty)
# 	a = 5.0
# 	logit = a * (m - difficulty)
# 	return _sigmoid(logit)


# def identify_gaps(user_id: str, threshold: float = 0.6) -> List[str]:
# 	m = estimate_mastery(user_id)
# 	return [c for c, v in sorted(m.items(), key=lambda x: x[1]) if v < threshold]


# def choose_difficulty(user_level: str, mastery: float) -> str:
# 	"""Return recommended difficulty label given user level and mastery."""
# 	# Map to textual difficulty used in resources (reusing 'level')
# 	if mastery < 0.5:
# 		return "beginner"
# 	if mastery < 0.75:
# 		return "intermediate"
# 	return "advanced"


# def recommend_remediation(user_id: str, goals: List[str], rag_engine, clip_indexer, style: str, k_text: int = 3, k_media: int = 6) -> Dict[str, Dict[str, List[Dict]]]:
# 	"""For each gap competency, recommend text chunks and media (images/frames)."""
# 	mastery = estimate_mastery(user_id)
# 	gaps = identify_gaps(user_id)
# 	out: Dict[str, Dict[str, List[Dict]]] = {}
# 	for comp in gaps:
# 		# Text recommendations: query tuned to competency and difficulty
# 		diff_label = choose_difficulty("", mastery.get(comp, 0.5))
# 		q = f"{comp} fundamentals examples"
# 		text_hits = rag_engine.query(q, k=k_text)
# 		# Filter by competency tag if present
# 		text_hits = [h for h in text_hits if comp in str(h['meta'].get('competencies',''))]
# 		if not text_hits:
# 			text_hits = rag_engine.query(f"explain {comp} step by step", k=k_text)

# 		# Media recommendations: text->image query hints
# 		media_q = f"{comp} diagram" if style == "visual" else f"{comp} concept"
# 		media_hits = clip_indexer.query(media_q, k=k_media)

# 		out[comp] = {"text": text_hits, "media": media_hits}
# 	return out




def estimate_mastery(user_id: str) -> Dict[str, float]:
    """Compute mastery per competency using an exponentially-weighted average of scores from progress and interactions."""
    alpha = 0.6  # weight for recent events
    mastery: Dict[str, float] = {}
    counts: Dict[str, float] = {}

    for topic, score in load_progress(user_id):
        mastery[topic] = mastery.get(topic, 0.0) * (1 - alpha) + score * alpha
        counts[topic] = counts.get(topic, 0.0) + 1

    for comp, score, difficulty, time_spent in load_interactions(user_id):
        adj = max(0.0, min(1.0, score - (difficulty - 0.5) * 0.2))
        mastery[comp] = mastery.get(comp, 0.0) * (1 - alpha) + adj * alpha
        counts[comp] = counts.get(comp, 0.0) + 1

    # Default unknown competencies to mid-level mastery
    for comp in ["arrays","linked-lists","stacks","queues","trees","graphs","dp"]:
        if comp not in mastery:
            mastery[comp] = 0.5
    return mastery

def predict_performance(user_id: str, competency: str, difficulty: float = 0.5) -> float:
    """Predict probability of success based on mastery and task difficulty (0..1)."""
    m = estimate_mastery(user_id).get(competency, 0.5)
    # Simple logistic: logit = a*(m - difficulty)
    a = 5.0
    logit = a * (m - difficulty)
    return _sigmoid(logit)

def identify_gaps(user_id: str, threshold: float = 0.6) -> List[str]:
    m = estimate_mastery(user_id)
    return [c for c, v in sorted(m.items(), key=lambda x: x[1]) if v < threshold]

def choose_difficulty(user_level: str, mastery: float) -> str:
    """Return recommended difficulty label given user level and mastery."""
    # Map to textual difficulty used in resources (reusing 'level')
    if mastery < 0.5:
        return "beginner"
    if mastery < 0.75:
        return "intermediate"
    return "advanced"

def recommend_remediation(user_id: str, goals: List[str], rag_engine, clip_indexer, style: str, k_text: int = 3, k_media: int = 6) -> Dict[str, Dict[str, List[Dict]]]:
    """For each gap competency, recommend text chunks and media (images/frames)."""
    mastery = estimate_mastery(user_id)
    gaps = identify_gaps(user_id)
    out: Dict[str, Dict[str, List[Dict]]] = {}
    for comp in gaps:
        # Text recommendations: query tuned to competency and difficulty
        diff_label = choose_difficulty("", mastery.get(comp, 0.5))
        q = f"{comp} fundamentals examples"
        text_hits = rag_engine.query(q, k=k_text)
        # Filter by competency tag if present
        text_hits = [h for h in text_hits if comp in str(h['meta'].get('competencies',''))]
        if not text_hits:
            text_hits = rag_engine.query(f"explain {comp} step by step", k=k_text)

        # Media recommendations: text->image query hints
        media_q = f"{comp} diagram" if style == "visual" else f"{comp} concept"
        media_hits = clip_indexer.query(media_q, k=k_media)

        out[comp] = {"text": text_hits, "media": media_hits}
    return out

def save_progress(user_id: str, topic: str, score: float):
    """Save user progress to database"""
    try:
        ensure_db_directory()
        if not os.path.exists(DB_PATH):
            init_db()
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO progress (user_id, topic, score) VALUES (?, ?, ?)",
            (user_id, topic, score)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving progress: {e}")
        return False

def save_interaction(user_id: str, competency: str, score: float, difficulty: float, time_spent: float):
    """Save user interaction to database"""
    try:
        ensure_db_directory()
        if not os.path.exists(DB_PATH):
            init_db()
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO interactions (user_id, competency, score, difficulty, time_spent) VALUES (?, ?, ?, ?, ?)",
            (user_id, competency, score, difficulty, time_spent)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving interaction: {e}")
        return Falsefrom typing import Dict, List, Tuple
from math import exp
import sqlite3
import os

# Create a writable directory for the database
DB_DIR = os.environ.get("DB_DIR", "./db")
DB_PATH = os.path.join(DB_DIR, "analytics.db")

def ensure_db_directory():
    """Ensure the database directory exists"""
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating database directory: {e}")
        return False

def init_db():
    """Initialize the database with required tables"""
    try:
        ensure_db_directory()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                score REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                competency TEXT NOT NULL,
                score REAL,
                difficulty REAL,
                time_spent REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

# Mastery and prediction utilities

def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + exp(-x))

def load_progress(user_id: str) -> List[Tuple[str, float]]:
    """Load user progress from database"""
    try:
        if not os.path.exists(DB_PATH):
            init_db()
            return []  # Return empty list for new users
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT topic, score FROM progress WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [(r[0], float(r[1])) for r in rows]
    except Exception as e:
        print(f"Error loading progress for user {user_id}: {e}")
        return []

def load_interactions(user_id: str) -> List[Tuple[str, float, float, float]]:
    """Returns (competency, score, difficulty, time_spent). If the table is missing, returns empty list."""
    try:
        if not os.path.exists(DB_PATH):
            init_db()
            return []
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT competency, score, difficulty, time_spent FROM interactions WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [(r[0], float(r[1] or 0.0), float(r[2] or 0.5), float(r[3] or 0.0)) for r in rows]
    except Exception as e:
        print(f"Error loading interactions for user {user_id}: {e}")
        return []
