from typing import List, Dict

def personalize_path(level: str, style: str, goals: List[str]) -> List[Dict]:
    """Generate personalized learning path based on user preferences"""
    
    # Define competency progression
    competency_paths = {
        "arrays": [
            {"topic": "Array Basics", "resources": ["array_intro", "array_operations"], "estimated_time": "2 hours"},
            {"topic": "Array Traversal", "resources": ["array_iteration", "array_search"], "estimated_time": "3 hours"},
            {"topic": "Array Algorithms", "resources": ["sorting", "two_pointers"], "estimated_time": "4 hours"}
        ],
        "linked-lists": [
            {"topic": "Linked List Basics", "resources": ["ll_intro", "ll_operations"], "estimated_time": "3 hours"},
            {"topic": "Linked List Traversal", "resources": ["ll_iteration", "ll_search"], "estimated_time": "2 hours"},
            {"topic": "Advanced Linked Lists", "resources": ["doubly_ll", "circular_ll"], "estimated_time": "4 hours"}
        ],
        "trees": [
            {"topic": "Tree Basics", "resources": ["tree_intro", "tree_traversal"], "estimated_time": "4 hours"},
            {"topic": "Binary Trees", "resources": ["binary_tree", "bst"], "estimated_time": "5 hours"},
            {"topic": "Advanced Trees", "resources": ["avl", "red_black"], "estimated_time": "6 hours"}
        ]
    }
    
    # Adjust difficulty based on level
    level_multipliers = {
        "beginner": 1.0,
        "intermediate": 0.7,
        "advanced": 0.5
    }
    
    # Style-based adjustments
    style_resources = {
        "visual": ["diagrams", "videos", "interactive"],
        "auditory": ["podcasts", "explanations", "audio"],
        "read/write": ["text", "notes", "exercises"],
        "kinesthetic": ["coding", "practice", "projects"]
    }
    
    path = []
    for goal in goals:
        if goal in competency_paths:
            for step in competency_paths[goal]:
                # Adjust time based on level
                adjusted_time = step["estimated_time"]
                if level in level_multipliers:
                    # Convert time string to hours, multiply, then back to string
                    time_parts = step["estimated_time"].split()
                    if len(time_parts) == 2 and time_parts[1] == "hours":
                        hours = float(time_parts[0]) * level_multipliers[level]
                        adjusted_time = f"{hours:.1f} hours"
                
                path.append({
                    "competency": goal,
                    "topic": step["topic"],
                    "resources": step["resources"] + style_resources.get(style, []),
                    "estimated_time": adjusted_time,
                    "level": level,
                    "style": style
                })
    
    return path
