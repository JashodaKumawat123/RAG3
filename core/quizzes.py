import os
import json
from typing import List, Dict, Any

QUIZ_DIR = os.path.join("content", "quizzes")


def list_quiz_files() -> List[str]:
    if not os.path.isdir(QUIZ_DIR):
        return []
    return [os.path.join(QUIZ_DIR, f) for f in os.listdir(QUIZ_DIR) if f.lower().endswith(".json")]


def load_quiz_packs() -> List[Dict[str, Any]]:
    packs: List[Dict[str, Any]] = []
    for path in list_quiz_files():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Expected keys: title, competency, level, questions: [{question, options, answer_index, difficulty?}]
                if isinstance(data, dict) and "questions" in data:
                    packs.append(data)
        except Exception:
            continue
    return packs


def grade_quiz(pack: Dict[str, Any], user_answers: List[int]) -> Dict[str, Any]:
    questions = pack.get("questions", [])
    total = len(questions)
    correct = 0
    detailed = []
    for i, q in enumerate(questions):
        ai = user_answers[i] if i < len(user_answers) else -1
        is_correct = int(ai) == int(q.get("answer_index", -999))
        if is_correct:
            correct += 1
        detailed.append({
            "question": q.get("question", ""),
            "selected": ai,
            "correct": int(q.get("answer_index", -1)),
            "is_correct": is_correct
        })
    score = (correct / total) if total > 0 else 0.0
    return {"score": score, "correct": correct, "total": total, "details": detailed}
