#!/usr/bin/env python3
"""
Test script for EduRAG multimodal functionality
"""

import os
import sys
from PIL import Image
import numpy as np

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_core_modules():
    """Test that all core modules can be imported"""
    print("Testing core module imports...")
    
    try:
        from core.rag import RAGEngine, format_context
        print("✓ RAGEngine imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import RAGEngine: {e}")
        return False
    
    try:
        from core.mm import CLIPIndexer
        print("✓ CLIPIndexer imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import CLIPIndexer: {e}")
        return False
    
    try:
        from core.user import upsert_user, get_user, log_progress, get_progress
        print("✓ User management functions imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import user functions: {e}")
        return False
    
    try:
        from core.path import personalize_path
        print("✓ Path personalization imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import path functions: {e}")
        return False
    
    return True

def test_rag_engine():
    """Test RAG engine functionality"""
    print("\nTesting RAG engine...")
    
    try:
        from core.rag import RAGEngine
        
        # Test CSV ingestion
        if os.path.exists("sample_resources.csv"):
            rag = RAGEngine()
            n_chunks = rag.ingest_csv("sample_resources.csv")
            print(f"✓ Ingested {n_chunks} text chunks")
            
            # Test query
            results = rag.query("array operations", k=3)
            print(f"✓ Retrieved {len(results)} results for 'array operations'")
            
            return True
        else:
            print("⚠ sample_resources.csv not found, skipping RAG test")
            return True
            
    except Exception as e:
        print(f"✗ RAG engine test failed: {e}")
        return False

def test_clip_indexer():
    """Test CLIP indexer functionality"""
    print("\nTesting CLIP indexer...")
    
    try:
        from core.mm import CLIPIndexer
        
        # Create a test image
        test_image = Image.new('RGB', (224, 224), color='red')
        
        # Initialize CLIP indexer
        clip = CLIPIndexer()
        print("✓ CLIPIndexer initialized")
        
        # Test image embedding
        embeddings = clip.embed_images([test_image])
        print(f"✓ Generated embeddings of shape: {embeddings.shape}")
        
        # Test text embedding
        text_embeddings = clip.embed_texts(["test query"])
        print(f"✓ Generated text embeddings of shape: {text_embeddings.shape}")
        
        return True
        
    except Exception as e:
        print(f"✗ CLIP indexer test failed: {e}")
        print("Note: This may fail if CLIP model is not downloaded yet")
        return False

def test_user_management():
    """Test user management functionality"""
    print("\nTesting user management...")
    
    try:
        from core.user import upsert_user, get_user, log_progress, get_progress
        
        # Test user operations
        test_user_id = "test_user_123"
        test_profile = {"level": "beginner", "style": "visual", "goals": ["arrays"]}
        
        upsert_user(test_user_id, test_profile)
        print("✓ User profile saved")
        
        retrieved_profile = get_user(test_user_id)
        if retrieved_profile and retrieved_profile.get("level") == "beginner":
            print("✓ User profile retrieved correctly")
        else:
            print("✗ User profile retrieval failed")
            return False
        
        # Test progress logging
        log_progress(test_user_id, "arrays", "started", 0.5)
        print("✓ Progress logged")
        
        progress = get_progress(test_user_id)
        if progress and len(progress) > 0:
            print(f"✓ Retrieved {len(progress)} progress entries")
        else:
            print("✗ Progress retrieval failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ User management test failed: {e}")
        return False

def test_learning_path():
    """Test learning path generation"""
    print("\nTesting learning path generation...")
    
    try:
        from core.path import personalize_path
        
        path = personalize_path("beginner", "visual", ["arrays", "trees"])
        
        if path and len(path) > 0:
            print(f"✓ Generated {len(path)} learning path steps")
            print(f"  First step: {path[0]['topic']} ({path[0]['competency']})")
        else:
            print("✗ Learning path generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Learning path test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing EduRAG Multimodal Extension")
    print("=" * 50)
    
    tests = [
        test_core_modules,
        test_rag_engine,
        test_clip_indexer,
        test_user_management,
        test_learning_path
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The multimodal extension is ready to use.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Upload sample_resources.csv in the Ingest tab")
        print("3. Try uploading some images/videos for multimodal search")
    else:
        print("⚠ Some tests failed. Check the output above for details.")
        print("\nCommon issues:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Ensure sample_resources.csv exists")
        print("- Check if CLIP model can be downloaded")

if __name__ == "__main__":
    main()
