import os
from typing import List, Dict, Optional
import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
import chromadb

PERSIST_DIR = os.environ.get("CHROMA_DIR","./chroma_store")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class CLIPIndexer:
    def __init__(self, collection_name="edurag_images", model_id: str="openai/clip-vit-base-patch32"):
        self.device = DEVICE
        self.model = CLIPModel.from_pretrained(model_id).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_id)
        self.client = chromadb.PersistentClient(path=PERSIST_DIR)
        # We'll store raw vectors; disable internal embedding function
        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception:
            self.collection = self.client.create_collection(collection_name)

    def embed_images(self, pil_images: List[Image.Image]) -> np.ndarray:
        inputs = self.processor(images=pil_images, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
        return image_features.cpu().numpy()

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        inputs = self.processor(text=texts, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
        return text_features.cpu().numpy()

    def add_images(self, items: List[Dict]):
        """items: list of dicts with keys: id, pil (PIL.Image), meta (dict)"""
        if not items: return 0
        imgs = [it["pil"] for it in items]
        embs = self.embed_images(imgs)
        ids = [it["id"] for it in items]
        metadatas = [it.get("meta",{}) for it in items]
        self.collection.add(ids=ids, embeddings=embs.tolist(), metadatas=metadatas, documents=["" for _ in ids])
        return len(ids)

    def query(self, text: str, k: int=8, where: Optional[Dict]=None):
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
