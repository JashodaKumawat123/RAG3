#!/usr/bin/env python3
"""
EduRAG Demo Script
Demonstrates the key features of the EduRAG system.
"""

import yaml
import json
from rag_pipeline import RAGPipeline
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
import time

console = Console()

def demo_retrieval(rag_pipeline):
    """Demonstrate RAG retrieval capabilities."""
    console.print(Panel.fit("🔍 RAG Retrieval Demo", style="bold blue"))
    
    test_queries = [
        "What is an array in data structures?",
        "How do linked lists work?",
        "Explain binary search algorithm",
        "What are the advantages of trees?",
        "How to implement a stack?"
    ]
    
    for query in test_queries:
        console.print(f"\n[bold]Query:[/bold] {query}")
        
        start_time = time.time()
        resources = rag_pipeline.retrieve(query, k=3)
        response_time = time.time() - start_time
        
        if resources:
            console.print(f"[green]Found {len(resources)} relevant resources in {response_time:.3f}s[/green]")
            
            for i, resource in enumerate(resources[:2], 1):  # Show top 2
                console.print(f"  {i}. {resource.title} (Score: {resource.score:.3f})")
                console.print(f"     Type: {resource.modality}, Topic: {resource.topic}")
        else:
            console.print("[red]No relevant resources found[/red]")
        
        time.sleep(0.5)  # Brief pause for readability

def demo_learning_path_generation(rag_pipeline):
    """Demonstrate learning path generation."""
    console.print(Panel.fit("🛤️ Learning Path Generation Demo", style="bold green"))
    
    # Test different user profiles
    test_users = [
        {
            'name': 'Beginner Student',
            'state': {
                'mastery': {},
                'vark_scores': {'visual': 0.7, 'auditory': 0.2, 'read_write': 0.1, 'kinesthetic': 0.0}
            }
        },
        {
            'name': 'Intermediate Student',
            'state': {
                'mastery': {'arrays': 0.8, 'strings': 0.7, 'searching': 0.6},
                'vark_scores': {'visual': 0.3, 'auditory': 0.1, 'read_write': 0.4, 'kinesthetic': 0.2}
            }
        },
        {
            'name': 'Advanced Student',
            'state': {
                'mastery': {'arrays': 0.9, 'linked_lists': 0.8, 'trees': 0.7, 'graphs': 0.6},
                'vark_scores': {'visual': 0.2, 'auditory': 0.1, 'read_write': 0.3, 'kinesthetic': 0.4}
            }
        }
    ]
    
    for user in test_users:
        console.print(f"\n[bold]User:[/bold] {user['name']}")
        console.print(f"[dim]Learning Style:[/dim] {max(user['state']['vark_scores'], key=user['state']['vark_scores'].get)}")
        console.print(f"[dim]Skills Mastered:[/dim] {len([m for m in user['state']['mastery'].values() if m >= 0.6])}")
        
        start_time = time.time()
        learning_path = rag_pipeline.plan_learning_path(user['state'], horizon_days=3)
        generation_time = time.time() - start_time
        
        if learning_path:
            console.print(f"[green]Generated {len(learning_path)}-day learning path in {generation_time:.3f}s[/green]")
            
            for day_idx, day in enumerate(learning_path, 1):
                console.print(f"  Day {day_idx}: {len(day.skills)} skills, {len(day.resources)} resources, {len(day.quizzes)} quizzes")
        else:
            console.print("[red]Failed to generate learning path[/red]")
        
        time.sleep(0.5)

def demo_quiz_generation(rag_pipeline):
    """Demonstrate quiz generation capabilities."""
    console.print(Panel.fit("🎯 Quiz Generation Demo", style="bold yellow"))
    
    # Load skills
    with open("models/skills.yaml", 'r') as f:
        skills = yaml.safe_load(f)['skills']
    
    # Test quiz generation for different skills
    test_skills = skills[:3]  # Test first 3 skills
    
    for skill in test_skills:
        console.print(f"\n[bold]Generating quiz for:[/bold] {skill['title']}")
        console.print(f"[dim]Difficulty:[/dim] {skill['difficulty']}/5, Level: {skill['level']}")
        
        start_time = time.time()
        quiz = rag_pipeline.generate_quiz(skill)
        generation_time = time.time() - start_time
        
        if quiz:
            console.print(f"[green]Generated quiz in {generation_time:.3f}s[/green]")
            console.print(f"  Question: {quiz.question[:100]}...")
            console.print(f"  Options: {len(quiz.options)} choices")
            console.print(f"  Explanation: {quiz.explanation[:50]}...")
        else:
            console.print("[red]Failed to generate quiz[/red]")
        
        time.sleep(0.5)

def demo_skill_tracking(rag_pipeline):
    """Demonstrate skill tracking and mastery updates."""
    console.print(Panel.fit("📊 Skill Tracking Demo", style="bold magenta"))
    
    # Simulate a student taking quizzes and improving
    user_state = {
        'mastery': {'arrays': 0.3, 'linked_lists': 0.1},
        'vark_scores': {'visual': 0.5, 'auditory': 0.2, 'read_write': 0.2, 'kinesthetic': 0.1}
    }
    
    console.print(f"[bold]Initial Mastery:[/bold]")
    for skill, mastery in user_state['mastery'].items():
        console.print(f"  {skill}: {mastery:.1%}")
    
    # Simulate quiz results
    quiz_results = [
        ('arrays', True, 1200),    # Correct answer, medium difficulty
        ('arrays', True, 1100),    # Correct answer, easier
        ('arrays', False, 1300),   # Wrong answer, harder
        ('linked_lists', True, 1000),  # Correct answer, easy
    ]
    
    console.print(f"\n[bold]Quiz Results:[/bold]")
    for skill, correct, difficulty in quiz_results:
        old_mastery = user_state['mastery'].get(skill, 0.0)
        
        # Update mastery using Elo-like algorithm
        new_rating = rag_pipeline.update_skill_rating(
            old_mastery * 1000,  # Convert to rating scale
            difficulty,
            1 if correct else 0
        )
        new_mastery = rag_pipeline.calculate_mastery(new_rating)
        user_state['mastery'][skill] = new_mastery
        
        status = "✅" if correct else "❌"
        console.print(f"  {status} {skill}: {old_mastery:.1%} → {new_mastery:.1%} (difficulty: {difficulty})")
    
    console.print(f"\n[bold]Final Mastery:[/bold]")
    for skill, mastery in user_state['mastery'].items():
        status = "🎯" if mastery >= 0.6 else "📈" if mastery >= 0.3 else "📚"
        console.print(f"  {status} {skill}: {mastery:.1%}")

def demo_learning_style_adaptation(rag_pipeline):
    """Demonstrate learning style adaptation."""
    console.print(Panel.fit("🎨 Learning Style Adaptation Demo", style="bold cyan"))
    
    # Test different learning styles
    test_styles = [
        ('Visual Learner', {'visual': 0.8, 'auditory': 0.1, 'read_write': 0.05, 'kinesthetic': 0.05}),
        ('Auditory Learner', {'visual': 0.1, 'auditory': 0.8, 'read_write': 0.05, 'kinesthetic': 0.05}),
        ('Read/Write Learner', {'visual': 0.1, 'auditory': 0.1, 'read_write': 0.8, 'kinesthetic': 0.0}),
        ('Kinesthetic Learner', {'visual': 0.1, 'auditory': 0.1, 'read_write': 0.1, 'kinesthetic': 0.7}),
    ]
    
    query = "Explain arrays in data structures"
    
    for style_name, vark_scores in test_styles:
        console.print(f"\n[bold]{style_name}:[/bold]")
        
        # Get resources
        resources = rag_pipeline.retrieve(query, k=5)
        
        # Filter by learning style
        learning_styles = rag_pipeline.get_learning_style(vark_scores)
        filtered_resources = rag_pipeline.filter_resources_by_style(resources, learning_styles)
        
        console.print(f"  Preferred styles: {', '.join(learning_styles)}")
        console.print(f"  Top 3 recommended resources:")
        
        for i, resource in enumerate(filtered_resources[:3], 1):
            console.print(f"    {i}. {resource.title} ({resource.modality}) - Score: {resource.score:.3f}")

def main():
    """Run the complete demo."""
    console.print(Panel.fit("🎓 EduRAG System Demo", style="bold white on blue"))
    console.print("This demo showcases the key features of the EduRAG system.\n")
    
    try:
        # Initialize RAG pipeline
        console.print("[yellow]Initializing RAG pipeline...[/yellow]")
        rag_pipeline = RAGPipeline(
            persist_dir="storage/chroma",
            skills_path="models/skills.yaml",
            prompts_path="models/prompts.yaml",
            styles_path="models/styles.yaml"
        )
        console.print("[green]✅ RAG pipeline initialized successfully[/green]\n")
        
        # Run demos
        demos = [
            ("RAG Retrieval", demo_retrieval),
            ("Learning Path Generation", demo_learning_path_generation),
            ("Quiz Generation", demo_quiz_generation),
            ("Skill Tracking", demo_skill_tracking),
            ("Learning Style Adaptation", demo_learning_style_adaptation),
        ]
        
        for demo_name, demo_func in demos:
            try:
                demo_func(rag_pipeline)
                console.print("\n" + "─" * 60 + "\n")
                time.sleep(1)
            except Exception as e:
                console.print(f"[red]Error in {demo_name}: {e}[/red]\n")
        
        # Final summary
        console.print(Panel.fit("🎉 Demo Complete!", style="bold green"))
        console.print("The EduRAG system successfully demonstrated:")
        console.print("• Intelligent content retrieval with relevance scoring")
        console.print("• Personalized learning path generation")
        console.print("• Adaptive quiz generation")
        console.print("• Skill mastery tracking with Elo-like updates")
        console.print("• Learning style-based resource filtering")
        console.print("\nReady to start learning? Run: streamlit run app.py")
        
    except Exception as e:
        console.print(f"[red]Failed to initialize demo: {e}[/red]")
        console.print("Make sure you've run the setup script first: python setup.py")

if __name__ == "__main__":
    main()