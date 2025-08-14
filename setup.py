#!/usr/bin/env python3
"""
EduRAG Setup Script
Automates the initial setup process for the EduRAG system.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version {sys.version.split()[0]} is compatible")
    return True

def create_directories():
    """Create necessary directories."""
    directories = [
        "storage/chroma",
        "content/notes",
        "content/videos",
        "content/quizzes",
        "state"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies."""
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def setup_virtual_environment():
    """Set up virtual environment."""
    if not os.path.exists(".venv"):
        return run_command("python -m venv .venv", "Creating virtual environment")
    else:
        print("✅ Virtual environment already exists")
        return True

def ingest_content():
    """Ingest and index content."""
    return run_command(
        "python data_ingest.py --content_dir content --persist_dir storage/chroma",
        "Ingesting and indexing content"
    )

def run_evaluation():
    """Run system evaluation."""
    return run_command(
        "python eval_rag.py --output evaluation_results.json",
        "Running system evaluation"
    )

def main():
    parser = argparse.ArgumentParser(description="Setup EduRAG system")
    parser.add_argument("--skip-eval", action="store_true", help="Skip evaluation step")
    parser.add_argument("--skip-ingest", action="store_true", help="Skip content ingestion")
    parser.add_argument("--force", action="store_true", help="Force reinstallation of dependencies")
    
    args = parser.parse_args()
    
    print("🚀 EduRAG Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if args.force or not os.path.exists(".venv/lib/site-packages/streamlit"):
        if not install_dependencies():
            sys.exit(1)
    else:
        print("✅ Dependencies already installed")
    
    # Ingest content
    if not args.skip_ingest:
        if not ingest_content():
            print("⚠️  Content ingestion failed, but continuing...")
    
    # Run evaluation
    if not args.skip_eval:
        if not run_evaluation():
            print("⚠️  Evaluation failed, but continuing...")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    print("   Windows: .venv\\Scripts\\activate")
    print("   macOS/Linux: source .venv/bin/activate")
    print("\n2. Run the application:")
    print("   streamlit run app.py")
    print("\n3. Open your browser to: http://localhost:8501")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()