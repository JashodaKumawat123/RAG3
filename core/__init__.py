"""
EduRAG Core Modules

This package contains the core functionality for the EduRAG multimodal system:
- RAG engine for text-based retrieval
- CLIP-based multimodal indexing
- User management and progress tracking
- Learning path personalization
"""

from .rag import RAGEngine, format_context
from .mm import CLIPIndexer
from .user import upsert_user, get_user, log_progress, get_progress
from .path import personalize_path

__all__ = [
    'RAGEngine',
    'format_context', 
    'CLIPIndexer',
    'upsert_user',
    'get_user',
    'log_progress',
    'get_progress',
    'personalize_path'
]
