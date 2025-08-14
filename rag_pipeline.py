from typing import List, Dict, Any, Optional
import yaml
import json
import numpy as np
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from dataclasses import dataclass
import math

@dataclass
class LearningResource:
    id: str
    title: str
    content: str
    modality: str
    topic: str
    difficulty: int
    source: str
    score: float

@dataclass
class QuizQuestion:
    question: str
    options: List[str]
    correct: int
    explanation: str
    difficulty: int

@dataclass
class LearningDay:
    skills: List[str]
    resources: List[LearningResource]
    quizzes: List[QuizQuestion]

class RAGPipeline:
    def __init__(self, persist_dir: str, skills_path: str, prompts_path: str, styles_path: str):
        """Initialize the RAG pipeline with ChromaDB and configuration."""
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection("edu_docs")
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        
        # Load configuration
        with open(skills_path, 'r') as f:
            self.skills = yaml.safe_load(f)
        with open(prompts_path, 'r') as f:
            self.prompts = yaml.safe_load(f)
        with open(styles_path, 'r') as f:
            self.styles = yaml.safe_load(f)
    
    def retrieve(self, query: str, k: int = 5, topic_filter: Optional[str] = None) -> List[LearningResource]:
        """Retrieve relevant documents from ChromaDB."""
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query).tolist()
            
            # Build query parameters
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": k,
                "include": ["documents", "metadatas", "distances", "ids"]
            }
            
            # Add topic filter if specified
            if topic_filter:
                query_params["where"] = {"topic": topic_filter}
            
            # Query ChromaDB
            results = self.collection.query(**query_params)
            
            # Convert to LearningResource objects
            resources = []
            for i in range(len(results["ids"][0])):
                resource = LearningResource(
                    id=results["ids"][0][i],
                    title=results["metadatas"][0][i].get("title", "Document"),
                    content=results["documents"][0][i],
                    modality=results["metadatas"][0][i].get("modality", "notes"),
                    topic=results["metadatas"][0][i].get("topic", "general"),
                    difficulty=results["metadatas"][0][i].get("difficulty", 1),
                    source=results["metadatas"][0][i].get("source", "unknown"),
                    score=1 - results["distances"][0][i]
                )
                resources.append(resource)
            
            return resources
        except Exception as e:
            print(f"Error in retrieval: {e}")
            return []
    
    def calculate_mastery(self, skill_rating: float) -> float:
        """Convert skill rating to mastery level (0-1)."""
        return 1 / (1 + math.exp(-(skill_rating - 1000) / 200))
    
    def update_skill_rating(self, current_rating: float, question_difficulty: int, 
                           result: int, k_factor: float = 32) -> float:
        """Update skill rating using Elo-like algorithm."""
        expected = 1 / (1 + 10 ** ((question_difficulty - current_rating) / 400))
        new_rating = current_rating + k_factor * (result - expected)
        return max(800, min(1400, new_rating))  # Clamp between 800-1400
    
    def get_learning_style(self, vark_scores: Dict[str, float]) -> List[str]:
        """Determine learning style from VARK scores."""
        sorted_styles = sorted(vark_scores.items(), key=lambda x: x[1], reverse=True)
        # Return top 2 styles if they're close, otherwise top 1
        if len(sorted_styles) > 1 and sorted_styles[0][1] - sorted_styles[1][1] < 0.2:
            return [sorted_styles[0][0], sorted_styles[1][0]]
        return [sorted_styles[0][0]]
    
    def filter_resources_by_style(self, resources: List[LearningResource], 
                                 learning_styles: List[str]) -> List[LearningResource]:
        """Filter resources based on learning style preferences."""
        if not learning_styles:
            return resources
        
        preferred_modalities = []
        for style in learning_styles:
            if style in self.styles["styles"]:
                preferred_modalities.extend(self.styles["styles"][style])
        
        # Score resources based on modality preference
        scored_resources = []
        for resource in resources:
            score = resource.score
            if resource.modality in preferred_modalities:
                score *= 1.5  # Boost preferred modalities
            scored_resources.append((resource, score))
        
        # Sort by score and return top resources
        scored_resources.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in scored_resources]
    
    def plan_learning_path(self, user_state: Dict[str, Any], horizon_days: int = 7) -> List[LearningDay]:
        """Generate a personalized learning path."""
        skills = self.skills["skills"]
        mastery = user_state.get("mastery", {})
        learning_styles = self.get_learning_style(user_state.get("vark_scores", {}))
        
        # Find skills that are ready to learn
        def is_ready(skill):
            return all(mastery.get(prereq, 0.0) >= 0.6 for prereq in skill.get("prerequisites", []))
        
        # Sort skills by level and difficulty
        ready_skills = [s for s in skills if is_ready(s)]
        ready_skills.sort(key=lambda x: (x.get("level", 5), x.get("difficulty", 5)))
        
        # Add remediation for low mastery skills
        remediation_skills = []
        for skill_id, skill_mastery in mastery.items():
            if skill_mastery < 0.6:
                skill_info = next((s for s in skills if s["id"] == skill_id), None)
                if skill_info:
                    remediation_skills.append(skill_info)
        
        # Combine and limit skills
        all_skills = remediation_skills + ready_skills
        skills_per_day = max(1, len(all_skills) // horizon_days)
        
        learning_path = []
        for day in range(horizon_days):
            day_skills = all_skills[day * skills_per_day:(day + 1) * skills_per_day]
            if not day_skills:
                break
            
            day_resources = []
            day_quizzes = []
            
            for skill in day_skills:
                # Get resources for this skill
                resources = self.retrieve(skill["description"], k=3, topic_filter=skill["id"])
                resources = self.filter_resources_by_style(resources, learning_styles)
                day_resources.extend(resources[:2])  # Limit to 2 resources per skill
                
                # Generate quiz for this skill
                quiz = self.generate_quiz(skill)
                if quiz:
                    day_quizzes.append(quiz)
            
            learning_day = LearningDay(
                skills=[s["id"] for s in day_skills],
                resources=day_resources,
                quizzes=day_quizzes
            )
            learning_path.append(learning_day)
        
        return learning_path
    
    def generate_quiz(self, skill: Dict[str, Any]) -> Optional[QuizQuestion]:
        """Generate a quiz question for a given skill."""
        try:
            # Retrieve relevant content for quiz generation
            resources = self.retrieve(skill["description"], k=2, topic_filter=skill["id"])
            if not resources:
                return None
            
            # Combine content for context
            context = "\n\n".join([r.content for r in resources])
            
            # For now, return a simple quiz question
            # In a full implementation, this would use an LLM to generate questions
            question = f"What is the main characteristic of {skill['title']}?"
            options = [
                f"Option A about {skill['title']}",
                f"Option B about {skill['title']}",
                f"Option C about {skill['title']}",
                f"Option D about {skill['title']}"
            ]
            
            return QuizQuestion(
                question=question,
                options=options,
                correct=0,
                explanation=f"This is the correct answer for {skill['title']}",
                difficulty=skill.get("difficulty", 2)
            )
        except Exception as e:
            print(f"Error generating quiz for {skill['id']}: {e}")
            return None
    
    def answer_question(self, question: str, topic_filter: Optional[str] = None) -> str:
        """Answer a student's question using RAG."""
        try:
            # Retrieve relevant context
            resources = self.retrieve(question, k=3, topic_filter=topic_filter)
            
            if not resources:
                return "I don't have enough information to answer that question."
            
            # Combine context
            context = "\n\n".join([r.content for r in resources])
            
            # For now, return a simple answer
            # In a full implementation, this would use an LLM
            answer = f"Based on the available information about {topic_filter or 'the topic'}, "
            answer += "here's what I found:\n\n"
            
            for i, resource in enumerate(resources, 1):
                answer += f"{i}. {resource.content[:200]}...\n"
                answer += f"   Source: {resource.source}\n\n"
            
            return answer
        except Exception as e:
            return f"Error generating answer: {e}"
    
    def get_skill_progress(self, user_id: str, skill_id: str) -> Dict[str, Any]:
        """Get progress information for a specific skill."""
        # This would typically query a database
        # For now, return mock data
        return {
            "skill_id": skill_id,
            "mastery": 0.5,
            "attempts": 3,
            "correct_answers": 2,
            "time_spent": 1200,  # seconds
            "last_practiced": "2024-01-15"
        }