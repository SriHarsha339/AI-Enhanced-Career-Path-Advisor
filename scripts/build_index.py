"""
Build FAISS index from knowledge base documents.
Run: python scripts/build_index.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag import RAGSystem


def main():
    print("=" * 60)
    print("Building FAISS Index from Knowledge Base")
    print("=" * 60)
    
    print("\n📦 Initializing RAG system...")
    rag = RAGSystem()
    
    print(f"✅ Index built successfully!")
    print(f"📊 Total documents indexed: {len(rag.metadata)}")
    print("\n✨ Index ready for recommendations!")


if __name__ == "__main__":
    main()
