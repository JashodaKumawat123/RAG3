import sqlite3
import os
from typing import Dict, List, Optional
from datetime import datetime

DB_PATH = "state/users.db"


def init_db():
    """Initialize the user database"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            profile_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            topic TEXT,
            status TEXT,
            score REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    # Create interactions table (for quiz attempts, practice, etc.)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            competency TEXT,
            score REAL,
            difficulty REAL,
            time_spent REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    conn.commit()
    conn.close()


def upsert_user(user_id: str, profile_data: Dict):
    """Create or update user profile"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    import json
    profile_json = json.dumps(profile_data)

    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, profile_data, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (user_id, profile_json))

    conn.commit()
    conn.close()


def get_user(user_id: str) -> Optional[Dict]:
    """Get user profile"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT profile_data FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        import json
        return json.loads(result[0])
    return None


def log_progress(user_id: str, topic: str, status: str, score: float):
    """Log user progress for a topic"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO progress (user_id, topic, status, score)
        VALUES (?, ?, ?, ?)
    ''', (user_id, topic, status, score))

    conn.commit()
    conn.close()


def log_interaction(user_id: str, competency: str, score: float, difficulty: float = 0.5, time_spent: float = 0.0):
    """Log an interaction (e.g., quiz attempt) that contributes to mastery analytics."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO interactions (user_id, competency, score, difficulty, time_spent)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, competency, score, difficulty, time_spent))

    conn.commit()
    conn.close()


def get_progress(user_id: str) -> List[Dict]:
    """Get user progress history"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT topic, status, score, timestamp
        FROM progress 
        WHERE user_id = ?
        ORDER BY timestamp DESC
    ''', (user_id,))

    results = cursor.fetchall()
    conn.close()

    progress = []
    for row in results:
        progress.append({
            'topic': row[0],
            'status': row[1],
            'score': row[2],
            'timestamp': row[3]
        })

    return progress
