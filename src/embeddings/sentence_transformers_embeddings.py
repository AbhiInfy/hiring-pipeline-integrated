import json
import logging
from typing import Optional, List, Dict, Tuple
import numpy as np
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class SentenceTransformersEmbeddingsService:
    """Service for generating embeddings using Sentence Transformers (local, free)."""

    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[Path] = None, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize Sentence Transformers embeddings service.

        Args:
            api_key: Not used (local model, no API key needed)
            cache_dir: Directory to cache embeddings (optional)
            model_name: Sentence Transformers model to use
        """
        self.api_key = api_key
        self.cache_dir = cache_dir
        self.model_name = model_name
        self.embedding_dim = 384  # all-MiniLM-L6-v2 uses 384 dimensions
        self._embedding_cache: Dict[str, np.ndarray] = {}
        self._model = None
        self._initialized = False

        if cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_cache()

    @property
    def model(self):
        """Lazy-load Sentence Transformers model."""
        if self._model is None and not self._initialized:
            self._initialized = True
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading Sentence Transformers model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Model loaded successfully. Embedding dimension: {self._model.get_sentence_embedding_dimension()}")
                self.embedding_dim = self._model.get_sentence_embedding_dimension()
            except ImportError:
                logger.error("sentence-transformers package not installed. Install with: pip install sentence-transformers")
            except Exception as e:
                logger.error(f"Failed to load Sentence Transformers model: {e}")
        return self._model

    def _text_hash(self, text: str) -> str:
        """Generate cache key from text."""
        return hashlib.md5(text.encode()).hexdigest()

    def _load_cache(self) -> None:
        """Load embeddings from disk cache."""
        if not self.cache_dir:
            return

        cache_file = self.cache_dir / "embeddings_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                    for key, val in cached.items():
                        self._embedding_cache[key] = np.array(val, dtype=np.float32)
                logger.info(f"Loaded {len(self._embedding_cache)} cached embeddings from disk")
            except Exception as e:
                logger.warning(f"Failed to load embedding cache: {e}")

    def _save_cache(self) -> None:
        """Save embeddings to disk cache."""
        if not self.cache_dir:
            return

        cache_file = self.cache_dir / "embeddings_cache.json"
        try:
            cache_data = {k: v.tolist() for k, v in self._embedding_cache.items()}
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            logger.debug(f"Saved {len(self._embedding_cache)} embeddings to cache")
        except Exception as e:
            logger.warning(f"Failed to save embedding cache: {e}")

    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding for a single text using Sentence Transformers.

        Args:
            text: Text to embed

        Returns:
            1D numpy array of embeddings, or None if generation fails
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to embed_text")
            return None

        text_hash = self._text_hash(text)

        if text_hash in self._embedding_cache:
            return self._embedding_cache[text_hash]

        embedding = None

        if self.model:
            try:
                embedding = self.model.encode(text, convert_to_numpy=True)
                embedding = embedding.astype(np.float32)
                logger.debug(f"Generated embedding via Sentence Transformers for hash {text_hash}")
            except Exception as e:
                logger.error(f"Failed to generate embedding via Sentence Transformers: {e}")
                embedding = None

        if embedding is None:
            logger.warning(f"Failed to generate embedding for text, returning None")
            return None

        self._embedding_cache[text_hash] = embedding.astype(np.float32)
        return self._embedding_cache[text_hash]

    def embed_batch(self, texts: List[str]) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for multiple texts (optimized batch processing).

        Args:
            texts: List of texts to embed

        Returns:
            Dictionary mapping text to embeddings
        """
        results = {}
        texts_to_encode = []
        text_keys = []

        # Check cache first
        for text in texts:
            text_hash = self._text_hash(text)
            if text_hash in self._embedding_cache:
                results[text] = self._embedding_cache[text_hash]
            else:
                texts_to_encode.append(text)
                text_keys.append((text, text_hash))

        # Batch encode uncached texts
        if texts_to_encode and self.model:
            try:
                embeddings = self.model.encode(texts_to_encode, convert_to_numpy=True, batch_size=32)
                for (text, text_hash), embedding in zip(text_keys, embeddings):
                    embedding = embedding.astype(np.float32)
                    self._embedding_cache[text_hash] = embedding
                    results[text] = embedding
                logger.info(f"Batch encoded {len(texts_to_encode)} texts")
            except Exception as e:
                logger.error(f"Failed to batch encode texts: {e}")
                for text in texts_to_encode:
                    embedding = self.embed_text(text)
                    if embedding is not None:
                        results[text] = embedding

        self._save_cache()
        return results

    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.

        Args:
            vec1: First embedding vector
            vec2: Second embedding vector

        Returns:
            Cosine similarity score (0-1)
        """
        if vec1 is None or vec2 is None:
            return 0.0

        vec1 = np.asarray(vec1, dtype=np.float32)
        vec2 = np.asarray(vec2, dtype=np.float32)

        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    def semantic_search(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: Dict[str, np.ndarray],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find top-k most similar candidates to query embedding.

        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: Dict mapping candidate names to embeddings
            top_k: Number of top results to return

        Returns:
            List of (candidate_name, similarity_score) tuples, sorted by similarity
        """
        if query_embedding is None or not candidate_embeddings:
            return []

        scores = []
        for name, embedding in candidate_embeddings.items():
            similarity = self.cosine_similarity(query_embedding, embedding)
            scores.append((name, similarity))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def clear_cache(self) -> None:
        """Clear in-memory and disk cache."""
        self._embedding_cache.clear()
        if self.cache_dir:
            cache_file = self.cache_dir / "embeddings_cache.json"
            if cache_file.exists():
                cache_file.unlink()
            logger.info("Embedding cache cleared")
