#!/usr/bin/env python3
"""
Vector Store - RAG layer for semantic search over ladder knowledge
Uses sentence-transformers for embeddings and FAISS for vector search
"""
import os
import json
import sqlite3
import pickle
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Run: pip install sentence-transformers")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    # Fallback to simple numpy search

class VectorStore:
    """Vector store for RAG over ladder knowledge"""

    def __init__(self, store_path: str = "rag/vectors", model_name: str = "all-MiniLM-L6-v2"):
        self.store_path = store_path
        self.model_name = model_name
        self.embedding_dim = 384  # MiniLM dimension

        # Create store directory
        os.makedirs(store_path, exist_ok=True)

        # Initialize embedding model
        if EMBEDDINGS_AVAILABLE:
            self.model = SentenceTransformer(model_name)
        else:
            self.model = None

        # Initialize or load index
        self.index = None
        self.documents: List[Dict] = []
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index or create new one"""
        index_path = os.path.join(self.store_path, "index.faiss")
        docs_path = os.path.join(self.store_path, "documents.pkl")

        if os.path.exists(index_path) and os.path.exists(docs_path):
            # Load existing
            if FAISS_AVAILABLE:
                self.index = faiss.read_index(index_path)
            else:
                self.index = np.load(index_path.replace('.faiss', '.npy'))

            with open(docs_path, 'rb') as f:
                self.documents = pickle.load(f)
        else:
            # Create new
            if FAISS_AVAILABLE:
                self.index = faiss.IndexFlatL2(self.embedding_dim)
            else:
                self.index = np.zeros((0, self.embedding_dim))
            self.documents = []

    def _save_index(self):
        """Save index to disk"""
        index_path = os.path.join(self.store_path, "index.faiss")
        docs_path = os.path.join(self.store_path, "documents.pkl")

        if FAISS_AVAILABLE:
            faiss.write_index(self.index, index_path)
        else:
            np.save(index_path.replace('.faiss', '.npy'), self.index)

        with open(docs_path, 'wb') as f:
            pickle.dump(self.documents, f)

    def embed(self, text: str) -> np.ndarray:
        """Embed text to vector"""
        if not self.model:
            # Fallback: random embedding (not useful, just for structure)
            return np.random.randn(self.embedding_dim).astype('float32')
        return self.model.encode(text, convert_to_numpy=True).astype('float32')

    def add_document(self, content: str, metadata: Dict = None):
        """Add a document to the store"""
        embedding = self.embed(content)

        # Add to index
        if FAISS_AVAILABLE:
            self.index.add(embedding.reshape(1, -1))
        else:
            self.index = np.vstack([self.index, embedding]) if len(self.index) > 0 else embedding.reshape(1, -1)

        # Store document
        doc = {
            "id": len(self.documents),
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        self.documents.append(doc)

        return doc["id"]

    def add_documents(self, documents: List[Dict]):
        """Add multiple documents (batch)"""
        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            self.add_document(content, metadata)

        self._save_index()

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Search for similar documents"""
        if len(self.documents) == 0:
            return []

        query_embedding = self.embed(query).reshape(1, -1)

        if FAISS_AVAILABLE:
            distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
            results = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(self.documents):
                    results.append((self.documents[idx], float(distances[0][i])))
            return results
        else:
            # Simple numpy search
            distances = np.linalg.norm(self.index - query_embedding, axis=1)
            indices = np.argsort(distances)[:top_k]
            return [(self.documents[i], float(distances[i])) for i in indices]

    def index_training_data(self, training_data_path: str):
        """Index training data JSON file"""
        with open(training_data_path) as f:
            data = json.load(f)

        for item in data:
            content = f"Q: {item['instruction']}\n"
            if item.get('input'):
                content += f"Context: {item['input']}\n"
            content += f"A: {item['output']}"

            self.add_document(content, {
                "type": "training_example",
                "instruction": item['instruction']
            })

        self._save_index()
        print(f"Indexed {len(data)} training examples")

    def index_memory_db(self, memory_db_path: str):
        """Index memory database (conversations, discoveries, learnings)"""
        conn = sqlite3.connect(memory_db_path)
        cur = conn.cursor()

        # Index discoveries
        cur.execute("SELECT category, title, content FROM discoveries")
        for row in cur.fetchall():
            content = f"Discovery [{row[0]}]: {row[1]}\n{row[2]}"
            self.add_document(content, {"type": "discovery", "category": row[0]})

        # Index learnings
        cur.execute("SELECT topic, insight, confidence FROM learnings")
        for row in cur.fetchall():
            content = f"Learning [{row[0]}] (confidence: {row[2]:.0%}): {row[1]}"
            self.add_document(content, {"type": "learning", "topic": row[0]})

        # Index high-importance progress events
        cur.execute("SELECT event_type, description FROM project_progress WHERE importance >= 7")
        for row in cur.fetchall():
            content = f"Progress [{row[0]}]: {row[1]}"
            self.add_document(content, {"type": "progress", "event_type": row[0]})

        conn.close()
        self._save_index()
        print(f"Indexed {len(self.documents)} total documents from memory")

    def get_context(self, query: str, max_tokens: int = 2000) -> str:
        """Get relevant context for a query"""
        results = self.search(query, top_k=5)

        context_parts = []
        total_len = 0

        for doc, score in results:
            content = doc['content']
            if total_len + len(content) > max_tokens * 4:  # Rough char to token
                break
            context_parts.append(f"[Relevance: {1/(1+score):.2f}]\n{content}")
            total_len += len(content)

        return "\n\n---\n\n".join(context_parts)


class RAGEngine:
    """High-level RAG engine combining vector store with LLM"""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def build_prompt(self, query: str, context: str) -> str:
        """Build a RAG prompt"""
        return f"""Use the following context to answer the question. If the context doesn't contain relevant information, say so.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""

    def query(self, question: str) -> Dict:
        """Query the RAG system"""
        # Get relevant context
        context = self.vector_store.get_context(question)

        # Build prompt
        prompt = self.build_prompt(question, context)

        return {
            "question": question,
            "context": context,
            "prompt": prompt,
            "sources": len(self.vector_store.search(question, top_k=5))
        }


# Standalone execution
if __name__ == "__main__":
    import sys

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    store_path = os.path.join(base_dir, "rag/vectors")

    store = VectorStore(store_path)

    if len(sys.argv) > 1 and sys.argv[1] == "index":
        # Index all data
        training_path = os.path.join(base_dir, "data/training_data.json")
        memory_path = os.path.join(base_dir, "db/memory.db")

        if os.path.exists(training_path):
            store.index_training_data(training_path)

        if os.path.exists(memory_path):
            store.index_memory_db(memory_path)

        print(f"Total documents indexed: {len(store.documents)}")

    elif len(sys.argv) > 1 and sys.argv[1] == "search":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "drift constant"
        results = store.search(query)
        print(f"Results for: {query}\n")
        for doc, score in results:
            print(f"[Score: {score:.4f}]")
            print(doc['content'][:200] + "...")
            print()
    else:
        print("Usage:")
        print("  python vector_store.py index    - Index all training data")
        print("  python vector_store.py search <query>  - Search for documents")
