import os
from typing import List, Dict, Optional
import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

# Fix SQLite version compatibility for ChromaDB
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import chromadb

PERSIST_DIR = os.environ.get("CHROMA_DIR", "./chroma_store")
# Force CPU for Streamlit Cloud compatibility to avoid tensor issues
DEVICE = "cpu"

class CLIPIndexer:
    def __init__(self, collection_name="edurag_images", model_id: str="openai/clip-vit-base-patch32"):
        self.device = DEVICE
        
        try:
            # Load model and processor without device transfer initially
            self.model = CLIPModel.from_pretrained(model_id)
            self.processor = CLIPProcessor.from_pretrained(model_id)
            
            # Only try to move to device if it's actually available and not CPU
            if self.device != "cpu" and torch.cuda.is_available():
                try:
                    self.model = self.model.to(self.device)
                except Exception as e:
                    print(f"Warning: Could not move model to {self.device}, using CPU: {e}")
                    self.device = "cpu"
            
        except Exception as e:
            print(f"Error loading CLIP model: {e}")
            raise e
            
        self.client = chromadb.PersistentClient(path=PERSIST_DIR)
        # We'll store raw vectors; disable internal embedding function
        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception:
            self.collection = self.client.create_collection(collection_name)

    def embed_images(self, pil_images: List[Image.Image]) -> np.ndarray:
        """Embed a list of PIL images"""
        try:
            inputs = self.processor(images=pil_images, return_tensors="pt", padding=True)
            
            # Move inputs to device if needed (but we're using CPU)
            if self.device != "cpu":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
            
            # Normalize features
            image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
            return image_features.cpu().numpy()
            
        except Exception as e:
            print(f"Error embedding images: {e}")
            # Return zero vectors as fallback
            return np.zeros((len(pil_images), 512))

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Embed a list of text strings"""
        try:
            inputs = self.processor(text=texts, return_tensors="pt", padding=True)
            
            # Move inputs to device if needed (but we're using CPU)
            if self.device != "cpu":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
            
            # Normalize features
            text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
            return text_features.cpu().numpy()
            
        except Exception as e:
            print(f"Error embedding texts: {e}")
            # Return zero vectors as fallback
            return np.zeros((len(texts), 512))

    def add_images(self, items: List[Dict]):
        """items: list of dicts with keys: id, pil (PIL.Image), meta (dict)"""
        if not items: 
            return 0
            
        try:
            imgs = [it["pil"] for it in items]
            embs = self.embed_images(imgs)
            ids = [it["id"] for it in items]
            metadatas = [it.get("meta", {}) for it in items]
            
            self.collection.add(
                ids=ids, 
                embeddings=embs.tolist(), 
                metadatas=metadatas, 
                documents=["" for _ in ids]
            )
            return len(ids)
            
        except Exception as e:
            print(f"Error adding images to collection: {e}")
            return 0

    def query(self, text: str, k: int = 8, where: Optional[Dict] = None):
        """Query the collection with text"""
        try:
            q = self.embed_texts([text])[0].tolist()
            
            # Only pass where parameter if it's not None and not empty
            query_kwargs = {"query_embeddings": [q], "n_results": k}
            if where and len(where) > 0:
                query_kwargs["where"] = where
                
            res = self.collection.query(**query_kwargs)
            
            out = []
            for i in range(len(res["ids"][0])):
                out.append({
                    "id": res["ids"][0][i],
                    "meta": res["metadatas"][0][i],
                    "dist": res["distances"][0][i],
                })
            return out
            
        except Exception as e:
            print(f"Error querying collection: {e}")
            return []
