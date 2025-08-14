import os
import pandas as pd

# Fix SQLite version compatibility for ChromaDB
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import chromadb
from typing import List, Dict, Optional

PERSIST_DIR = os.environ.get("CHROMA_DIR","./chroma_store")

class RAGEngine:
    def __init__(self, collection_name="edurag_text"):
        self.client = chromadb.PersistentClient(path=PERSIST_DIR)
        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception:
            self.collection = self.client.create_collection(collection_name)
    
    def ingest_csv(self, csv_path: str) -> int:
        """Ingest CSV with columns: id, title, type, url, content, competencies, level"""
        df = pd.read_csv(csv_path)
        if df.empty:
            return 0
        
        # Simple text chunking (can be enhanced with proper chunking)
        documents = []
        metadatas = []
        ids = []
        
        for _, row in df.iterrows():
            content = str(row.get('content', ''))
            if len(content) > 1000:  # Simple chunking
                chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{row.get('id', 'doc')}_{i}"
                    documents.append(chunk)
                    metadatas.append({
                        'title': row.get('title', ''),
                        'type': row.get('type', 'text'),
                        'url': row.get('url', ''),
                        'competencies': row.get('competencies', ''),
                        'level': row.get('level', 'beginner'),
                        'chunk_id': i
                    })
                    ids.append(chunk_id)
            else:
                documents.append(content)
                metadatas.append({
                    'title': row.get('title', ''),
                    'type': row.get('type', 'text'),
                    'url': row.get('url', ''),
                    'competencies': row.get('competencies', ''),
                    'level': row.get('level', 'beginner'),
                    'chunk_id': 0
                })
                ids.append(str(row.get('id', 'doc')))
        
        if documents:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        
        return len(documents)
    
    def query(self, text: str, k: int = 5, where: Optional[Dict] = None) -> List[Dict]:
        """Query the collection and return results"""
        query_params = {
            "query_texts": [text],
            "n_results": k
        }
        if where:
            query_params["where"] = where
            
        results = self.collection.query(**query_params)
        
        hits = []
        for i in range(len(results['ids'][0])):
            hits.append({
                'id': results['ids'][0][i],
                'doc': results['documents'][0][i],
                'meta': results['metadatas'][0][i],
                'dist': results['distances'][0][i] if 'distances' in results else 0.0
            })
        
        return hits

def format_context(hits: List[Dict]) -> str:
    """Format retrieved context for LLM input"""
    context_parts = []
    for hit in hits:
        context_parts.append(f"Source: {hit['meta'].get('title', 'Unknown')}\nContent: {hit['doc']}\n")
    return "\n".join(context_parts)
