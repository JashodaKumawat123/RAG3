import argparse
import time
import json
import yaml
from typing import List, Dict, Any
from rag_pipeline import RAGPipeline
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()

class RAGEvaluator:
    def __init__(self, persist_dir: str, skills_path: str, prompts_path: str, styles_path: str):
        """Initialize the RAG evaluator."""
        self.rag_pipeline = RAGPipeline(persist_dir, skills_path, prompts_path, styles_path)
        
    def evaluate_retrieval(self, test_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate retrieval performance."""
        console.print("[bold blue]Evaluating Retrieval Performance[/bold blue]")
        
        results = {
            'total_queries': len(test_queries),
            'avg_response_time': 0,
            'avg_relevance_score': 0,
            'success_rate': 0,
            'detailed_results': []
        }
        
        total_time = 0
        total_relevance = 0
        successful_queries = 0
        
        for query_data in track(test_queries, description="Evaluating queries"):
            query = query_data['query']
            expected_topic = query_data.get('expected_topic')
            
            start_time = time.time()
            try:
                resources = self.rag_pipeline.retrieve(query, k=5, topic_filter=expected_topic)
                response_time = time.time() - start_time
                
                # Calculate relevance score (simple heuristic)
                relevance_score = 0
                if resources:
                    relevance_score = sum(r.score for r in resources) / len(resources)
                    successful_queries += 1
                
                total_time += response_time
                total_relevance += relevance_score
                
                results['detailed_results'].append({
                    'query': query,
                    'response_time': response_time,
                    'relevance_score': relevance_score,
                    'num_results': len(resources),
                    'success': len(resources) > 0
                })
                
            except Exception as e:
                console.print(f"[red]Error evaluating query '{query}': {e}[/red]")
                results['detailed_results'].append({
                    'query': query,
                    'response_time': 0,
                    'relevance_score': 0,
                    'num_results': 0,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate averages
        if results['total_queries'] > 0:
            results['avg_response_time'] = total_time / results['total_queries']
            results['avg_relevance_score'] = total_relevance / results['total_queries']
            results['success_rate'] = successful_queries / results['total_queries']
        
        return results
    
    def evaluate_learning_path_generation(self, test_users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate learning path generation."""
        console.print("[bold blue]Evaluating Learning Path Generation[/bold blue]")
        
        results = {
            'total_users': len(test_users),
            'avg_path_length': 0,
            'avg_generation_time': 0,
            'success_rate': 0,
            'detailed_results': []
        }
        
        total_time = 0
        total_path_length = 0
        successful_generations = 0
        
        for user_data in track(test_users, description="Generating learning paths"):
            start_time = time.time()
            try:
                learning_path = self.rag_pipeline.plan_learning_path(user_data['user_state'])
                generation_time = time.time() - start_time
                
                if learning_path:
                    path_length = len(learning_path)
                    total_path_length += path_length
                    successful_generations += 1
                    
                    results['detailed_results'].append({
                        'user_id': user_data.get('user_id', 'unknown'),
                        'generation_time': generation_time,
                        'path_length': path_length,
                        'success': True,
                        'skills_covered': sum(len(day.skills) for day in learning_path)
                    })
                else:
                    results['detailed_results'].append({
                        'user_id': user_data.get('user_id', 'unknown'),
                        'generation_time': generation_time,
                        'path_length': 0,
                        'success': False
                    })
                
                total_time += generation_time
                
            except Exception as e:
                console.print(f"[red]Error generating path for user {user_data.get('user_id', 'unknown')}: {e}[/red]")
                results['detailed_results'].append({
                    'user_id': user_data.get('user_id', 'unknown'),
                    'generation_time': 0,
                    'path_length': 0,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate averages
        if results['total_users'] > 0:
            results['avg_generation_time'] = total_time / results['total_users']
            results['success_rate'] = successful_generations / results['total_users']
        
        if successful_generations > 0:
            results['avg_path_length'] = total_path_length / successful_generations
        
        return results
    
    def evaluate_quiz_generation(self, test_skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate quiz generation performance."""
        console.print("[bold blue]Evaluating Quiz Generation[/bold blue]")
        
        results = {
            'total_skills': len(test_skills),
            'success_rate': 0,
            'avg_generation_time': 0,
            'detailed_results': []
        }
        
        total_time = 0
        successful_generations = 0
        
        for skill_data in track(test_skills, description="Generating quizzes"):
            skill = skill_data['skill']
            
            start_time = time.time()
            try:
                quiz = self.rag_pipeline.generate_quiz(skill)
                generation_time = time.time() - start_time
                
                if quiz:
                    successful_generations += 1
                    results['detailed_results'].append({
                        'skill_id': skill['id'],
                        'skill_title': skill['title'],
                        'generation_time': generation_time,
                        'success': True,
                        'has_question': bool(quiz.question),
                        'has_options': len(quiz.options) > 0,
                        'has_explanation': bool(quiz.explanation)
                    })
                else:
                    results['detailed_results'].append({
                        'skill_id': skill['id'],
                        'skill_title': skill['title'],
                        'generation_time': generation_time,
                        'success': False
                    })
                
                total_time += generation_time
                
            except Exception as e:
                console.print(f"[red]Error generating quiz for skill {skill['id']}: {e}[/red]")
                results['detailed_results'].append({
                    'skill_id': skill['id'],
                    'skill_title': skill['title'],
                    'generation_time': 0,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate averages
        if results['total_skills'] > 0:
            results['avg_generation_time'] = total_time / results['total_skills']
            results['success_rate'] = successful_generations / results['total_skills']
        
        return results
    
    def print_results(self, results: Dict[str, Any], evaluation_type: str):
        """Print evaluation results in a formatted table."""
        console.print(f"\n[bold green]📊 {evaluation_type} Results[/bold green]")
        
        # Summary table
        summary_table = Table(title=f"{evaluation_type} Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta")
        
        for key, value in results.items():
            if not key.endswith('_results'):
                if isinstance(value, float):
                    summary_table.add_row(key.replace('_', ' ').title(), f"{value:.3f}")
                else:
                    summary_table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(summary_table)
        
        # Detailed results table (first 5 entries)
        if results.get('detailed_results'):
            console.print(f"\n[bold yellow]📋 Sample Detailed Results (showing first 5)[/bold yellow]")
            detail_table = Table(title="Detailed Results")
            
            # Get column names from first result
            first_result = results['detailed_results'][0]
            for col in first_result.keys():
                detail_table.add_column(col, style="cyan")
            
            # Add rows
            for result in results['detailed_results'][:5]:
                detail_table.add_row(*[str(v) for v in result.values()])
            
            console.print(detail_table)

def create_test_data():
    """Create test data for evaluation."""
    # Test queries for retrieval evaluation
    test_queries = [
        {
            'query': 'What is an array in data structures?',
            'expected_topic': 'arrays'
        },
        {
            'query': 'How do linked lists work?',
            'expected_topic': 'linked_lists'
        },
        {
            'query': 'Explain binary search algorithm',
            'expected_topic': 'searching'
        },
        {
            'query': 'What are the advantages of trees?',
            'expected_topic': 'trees'
        },
        {
            'query': 'How to implement a stack?',
            'expected_topic': 'stacks_queues'
        }
    ]
    
    # Test users for learning path evaluation
    test_users = [
        {
            'user_id': 'beginner_1',
            'user_state': {
                'mastery': {},
                'vark_scores': {'visual': 0.7, 'auditory': 0.2, 'read_write': 0.1, 'kinesthetic': 0.0}
            }
        },
        {
            'user_id': 'intermediate_1',
            'user_state': {
                'mastery': {'arrays': 0.8, 'strings': 0.7, 'searching': 0.6},
                'vark_scores': {'visual': 0.3, 'auditory': 0.1, 'read_write': 0.4, 'kinesthetic': 0.2}
            }
        },
        {
            'user_id': 'advanced_1',
            'user_state': {
                'mastery': {'arrays': 0.9, 'linked_lists': 0.8, 'trees': 0.7, 'graphs': 0.6},
                'vark_scores': {'visual': 0.2, 'auditory': 0.1, 'read_write': 0.3, 'kinesthetic': 0.4}
            }
        }
    ]
    
    # Test skills for quiz evaluation
    skills = yaml.safe_load(open("models/skills.yaml", 'r'))['skills']
    test_skills = [{'skill': skill} for skill in skills[:5]]  # Test first 5 skills
    
    return test_queries, test_users, test_skills

def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate EduRAG system performance")
    parser.add_argument("--persist_dir", default="storage/chroma", help="ChromaDB persistence directory")
    parser.add_argument("--skills_path", default="models/skills.yaml", help="Skills configuration file")
    parser.add_argument("--prompts_path", default="models/prompts.yaml", help="Prompts configuration file")
    parser.add_argument("--styles_path", default="models/styles.yaml", help="Styles configuration file")
    parser.add_argument("--output", help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    console.print("[bold blue]🚀 Starting EduRAG Evaluation[/bold blue]")
    
    try:
        # Initialize evaluator
        evaluator = RAGEvaluator(args.persist_dir, args.skills_path, args.prompts_path, args.styles_path)
        
        # Create test data
        test_queries, test_users, test_skills = create_test_data()
        
        # Run evaluations
        all_results = {}
        
        # 1. Retrieval evaluation
        retrieval_results = evaluator.evaluate_retrieval(test_queries)
        evaluator.print_results(retrieval_results, "Retrieval")
        all_results['retrieval'] = retrieval_results
        
        # 2. Learning path evaluation
        path_results = evaluator.evaluate_learning_path_generation(test_users)
        evaluator.print_results(path_results, "Learning Path Generation")
        all_results['learning_path'] = path_results
        
        # 3. Quiz generation evaluation
        quiz_results = evaluator.evaluate_quiz_generation(test_skills)
        evaluator.print_results(quiz_results, "Quiz Generation")
        all_results['quiz_generation'] = quiz_results
        
        # Overall summary
        console.print("\n[bold green]🎯 Overall Performance Summary[/bold green]")
        overall_table = Table(title="Overall Performance")
        overall_table.add_column("Component", style="cyan")
        overall_table.add_column("Success Rate", style="magenta")
        overall_table.add_column("Avg Response Time", style="yellow")
        
        overall_table.add_row(
            "Retrieval",
            f"{retrieval_results['success_rate']:.1%}",
            f"{retrieval_results['avg_response_time']:.3f}s"
        )
        overall_table.add_row(
            "Learning Path",
            f"{path_results['success_rate']:.1%}",
            f"{path_results['avg_generation_time']:.3f}s"
        )
        overall_table.add_row(
            "Quiz Generation",
            f"{quiz_results['success_rate']:.1%}",
            f"{quiz_results['avg_generation_time']:.3f}s"
        )
        
        console.print(overall_table)
        
        # Save results if output file specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(all_results, f, indent=2)
            console.print(f"[green]Results saved to {args.output}[/green]")
        
        console.print("\n[bold green]✅ Evaluation complete![/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error during evaluation: {e}[/red]")

if __name__ == "__main__":
    main()