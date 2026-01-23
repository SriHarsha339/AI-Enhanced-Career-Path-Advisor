"""
RAG system: FAISS indexing and retrieval.
"""
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.config import (
    EMBEDDING_MODEL,
    FAISS_INDEX_FILE,
    FAISS_METADATA_FILE,
    KB_DOCS_DIR,
    RETRIEVAL_TOP_K
)


class RAGSystem:
    """RAG system for evidence retrieval."""

    def __init__(self):
        """Initialize embeddings model."""
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.metadata = []
        self.load_or_build_index()

    def load_or_build_index(self):
        """Load existing index or build from scratch."""
        if FAISS_INDEX_FILE.exists() and FAISS_METADATA_FILE.exists():
            self.load_index()
        else:
            self.build_index_from_docs()

    def load_index(self):
        """Load FAISS index from disk."""
        try:
            import faiss
            self.index = faiss.read_index(str(FAISS_INDEX_FILE))
            with open(FAISS_METADATA_FILE, "r") as f:
                self.metadata = json.load(f)
            print(f"Loaded FAISS index with {len(self.metadata)} documents")
        except Exception as e:
            print(f"Error loading index: {e}. Building from scratch...")
            self.build_index_from_docs()

    def build_index_from_docs(self):
        """Build FAISS index from knowledge base documents."""
        import faiss
        
        if not KB_DOCS_DIR.exists():
            print(f"Warning: KB docs directory not found at {KB_DOCS_DIR}")
            # Create minimal index
            self._create_minimal_index()
            return
        
        docs = self._load_kb_docs()
        if not docs:
            print("No KB documents found. Creating minimal index...")
            self._create_minimal_index()
            return
        
        # Embed all documents
        texts = [d["text"] for d in docs]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8)
        
        # Build FAISS index (inner product on normalized = cosine)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings.astype(np.float32))
        
        # Save metadata and index
        self.metadata = docs
        self.save_index()
        print(f"Built FAISS index with {len(docs)} documents")

    def _load_kb_docs(self) -> List[Dict[str, Any]]:
        """Load all documents from KB directory."""
        docs = []
        chunk_id = 0
        
        for file_path in KB_DOCS_DIR.glob("*.txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Simple chunking: split by paragraphs
            paragraphs = content.split("\n\n")
            for para in paragraphs:
                if para.strip():
                    docs.append({
                        "chunk_id": f"{file_path.stem}_{chunk_id}",
                        "text": para.strip(),
                        "source": file_path.name,
                        "category": self._infer_category(file_path.name)
                    })
                    chunk_id += 1
        
        return docs

    def _infer_category(self, filename: str) -> str:
        """Infer document category from filename."""
        filename_lower = filename.lower()
        if "role" in filename_lower or "job" in filename_lower:
            return "role"
        elif "resource" in filename_lower or "learn" in filename_lower:
            return "resource"
        else:
            return "market"

    def _create_minimal_index(self):
        """Create a minimal index with default content."""
        import faiss
        
        default_docs = [
            "Career development involves continuous learning and skill enhancement throughout your professional journey.",
            "Different career paths require different combinations of technical and soft skills.",
            "The job market is evolving with emerging technologies and new industries.",
            "Networking and building professional relationships is crucial for career growth.",
            "Work-life balance and remote opportunities have become increasingly important in modern careers.",
            "Specialization versus generalization - both paths have their advantages in different fields.",
            "Mentorship and guidance can significantly accelerate career progression.",
            "Personal branding and portfolio building help showcase your expertise to potential employers.",
            "Upskilling and reskilling are essential for staying relevant in a changing job market.",
            "Career transitions are possible at any stage with proper planning and preparation.",
        ]
        
        embeddings = self.model.encode(default_docs, convert_to_numpy=True)
        embeddings = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings.astype(np.float32))
        
        self.metadata = [
            {
                "chunk_id": f"default_{i}",
                "text": doc,
                "source": "default.txt",
                "category": "resource"
            }
            for i, doc in enumerate(default_docs)
        ]
        
        self.save_index()

    def save_index(self):
        """Save FAISS index to disk."""
        import faiss
        FAISS_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(FAISS_INDEX_FILE))
        with open(FAISS_METADATA_FILE, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def retrieve(
        self,
        query: str,
        top_k: int = RETRIEVAL_TOP_K,
        category_filter: str = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k evidence chunks for a query.
        Optionally filter by category (role, market, resource).
        """
        if self.index is None or not self.metadata:
            return []
        
        # Embed query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        query_embedding = query_embedding / (np.linalg.norm(query_embedding, axis=1, keepdims=True) + 1e-8)
        
        # Search
        k_search = min(top_k * 3, len(self.metadata))  # Over-fetch to account for filtering
        distances, indices = self.index.search(query_embedding.astype(np.float32), k_search)
        
        results = []
        for idx in indices[0]:
            if idx >= len(self.metadata):
                continue
            
            doc = self.metadata[idx]
            
            # Apply category filter if specified
            if category_filter and doc.get("category") != category_filter:
                continue
            
            results.append(doc)
            if len(results) >= top_k:
                break
        
        return results

    def retrieve_for_career(
        self,
        career_title: str,
        career_keywords: List[str],
        user_interests: List[str],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve evidence specific to a career.
        Tries role + market snippets.
        """
        # Construct query combining career info and user interests
        query_parts = [career_title] + career_keywords[:3] + user_interests[:2]
        query = " ".join(query_parts)
        
        # Retrieve role-related snippets
        role_evidence = self.retrieve(query, top_k=top_k // 2, category_filter="role")
        
        # Retrieve market/resource snippets
        market_evidence = self.retrieve(query, top_k=top_k // 2, category_filter="market")
        
        return role_evidence + market_evidence
