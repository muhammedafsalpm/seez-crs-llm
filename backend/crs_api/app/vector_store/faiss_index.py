import numpy as np
import faiss
from typing import List, Tuple, Optional
import pickle
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """Efficient vector store using FAISS"""
    
    def __init__(self, dimension: int = 384, index_path: Optional[Path] = None):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine with normalized vectors)
        self.metadata: List[dict] = []
        self.texts: List[str] = []
        self.normalized = False
        
        if index_path and index_path.exists():
            self.load(index_path)
    
    def add(self, vectors: np.ndarray, texts: List[str], metadata: List[dict]):
        """Add vectors to index"""
        if len(vectors) == 0:
            return
        
        # Normalize for cosine similarity
        vectors = vectors.astype(np.float32)
        faiss.normalize_L2(vectors)
        
        self.index.add(vectors)
        self.texts.extend(texts)
        self.metadata.extend(metadata)
        logger.info(f"Added {len(vectors)} vectors. Total: {self.index.ntotal}")
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[str, dict, float]]:
        """Search for similar vectors"""
        if self.index.ntotal == 0:
            return []
        
        # Normalize query
        query_vector = query_vector.astype(np.float32).reshape(1, -1)
        faiss.normalize_L2(query_vector)
        
        # Search
        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.texts):
                similarity = float(distances[0][i])
                results.append((self.texts[idx], self.metadata[idx], similarity))
        
        return results
    
    def save(self, path: Path):
        """Save index and metadata"""
        path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(path / "index.faiss"))
        
        # Save metadata
        with open(path / "metadata.pkl", 'wb') as f:
            pickle.dump({
                'texts': self.texts,
                'metadata': self.metadata,
                'dimension': self.dimension
            }, f)
        
        logger.info(f"Saved index to {path}")
    
    def load(self, path: Path):
        """Load index and metadata"""
        # Load FAISS index
        self.index = faiss.read_index(str(path / "index.faiss"))
        
        # Load metadata
        with open(path / "metadata.pkl", 'rb') as f:
            data = pickle.load(f)
            self.texts = data['texts']
            self.metadata = data['metadata']
            self.dimension = data['dimension']
        
        logger.info(f"Loaded index with {self.index.ntotal} vectors")
