import argparse
import os
import glob
import uuid
import json
import yaml
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from rich.console import Console
from rich.progress import track

console = Console()
MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def chunk_text(text, max_tokens=400):
    """Split text into chunks of approximately max_tokens words."""
    parts = []
    lines = text.split('\n')
    buf = []
    size = 0
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        words = line.split()
        size += len(words)
        buf.append(line)
        
        if size >= max_tokens:
            parts.append('\n'.join(buf))
            buf = []
            size = 0
    
    if buf:
        parts.append('\n'.join(buf))
    
    return parts

def load_docs(content_dir):
    """Load documents from various sources in the content directory."""
    docs = []
    
    # Load markdown and text files
    for path in glob.glob(os.path.join(content_dir, "**/*.*"), recursive=True):
        if any(path.endswith(ext) for ext in [".md", ".txt"]):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    if text.strip():  # Only add non-empty documents
                        # Extract topic from path
                        topic = os.path.basename(os.path.dirname(path))
                        if topic == "notes":
                            topic = os.path.splitext(os.path.basename(path))[0]
                        
                        docs.append({
                            "id": str(uuid.uuid4()),
                            "text": text,
                            "meta": {
                                "source": path,
                                "modality": "notes",
                                "topic": topic,
                                "type": "documentation"
                            }
                        })
            except Exception as e:
                console.print(f"[red]Error reading {path}: {e}[/red]")
    
    # Load video links
    links_path = os.path.join(content_dir, "videos", "links.json")
    if os.path.exists(links_path):
        try:
            with open(links_path, "r", encoding="utf-8") as f:
                links = json.load(f)
                for item in links:
                    text = f"{item['title']}\n\n{item.get('summary', '')}"
                    docs.append({
                        "id": str(uuid.uuid4()),
                        "text": text,
                        "meta": {
                            "source": item["url"],
                            "modality": "video",
                            "topic": item.get("topics", ["general"])[0],
                            "type": "video",
                            "duration": item.get("duration", ""),
                            "difficulty": item.get("difficulty", 1)
                        }
                    })
        except Exception as e:
            console.print(f"[red]Error reading video links: {e}[/red]")
    
    return docs

def main(args):
    """Main ingestion function."""
    console.print("[bold blue]Starting EduRAG Data Ingestion[/bold blue]")
    
    # Initialize ChromaDB
    console.print(f"[yellow]Initializing ChromaDB at {args.persist_dir}[/yellow]")
    client = chromadb.PersistentClient(
        path=args.persist_dir, 
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    collection = client.get_or_create_collection(
        name="edu_docs", 
        metadata={"hnsw:space": "cosine"}
    )
    
    # Load embedding model
    console.print("[yellow]Loading embedding model...[/yellow]")
    model = SentenceTransformer(MODEL)
    
    # Load documents
    console.print(f"[yellow]Loading documents from {args.content_dir}[/yellow]")
    docs = load_docs(args.content_dir)
    console.print(f"[green]Loaded {len(docs)} documents[/green]")
    
    if not docs:
        console.print("[red]No documents found![/red]")
        return
    
    # Process and index documents
    console.print("[yellow]Processing and indexing documents...[/yellow]")
    total_chunks = 0
    
    for doc in track(docs, description="Processing documents"):
        chunks = chunk_text(doc["text"])
        total_chunks += len(chunks)
        
        for i, chunk in enumerate(chunks):
            if chunk.strip():  # Only index non-empty chunks
                try:
                    # Generate embedding
                    embedding = model.encode(chunk).tolist()
                    
                    # Create unique ID for chunk
                    chunk_id = f"{doc['id']}-{i}"
                    
                    # Add to collection
                    collection.add(
                        ids=[chunk_id],
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[doc["meta"]]
                    )
                except Exception as e:
                    console.print(f"[red]Error processing chunk {i} of {doc['id']}: {e}[/red]")
    
    # Print summary
    final_count = collection.count()
    console.print(f"[bold green]✅ Ingestion complete![/bold green]")
    console.print(f"[green]Indexed {final_count} chunks from {len(docs)} documents[/green]")
    console.print(f"[green]Storage location: {args.persist_dir}[/green]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest content for EduRAG system")
    parser.add_argument(
        "--content_dir", 
        required=True, 
        help="Directory containing content files"
    )
    parser.add_argument(
        "--persist_dir", 
        required=True, 
        help="Directory to store ChromaDB data"
    )
    
    args = parser.parse_args()
    main(args)