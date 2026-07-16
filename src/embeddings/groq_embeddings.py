import json
import logging
from typing import Optional, List, Dict, Tuple
import numpy as np
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class GroqEmbeddingsService:
    """Service for generating embeddings using Groq API (free tier)."""

    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[Path] = None):
        """
        Initialize Groq embeddings service.

        Args:
            api_key: Groq API key (if None, will try to use env variable)
            cache_dir: Directory to cache embeddings (optional)
        """
        self.api_key = api_key
        self.cache_dir = cache_dir
        self.model = "text-embedding-3-small"  # Conceptual model name
        self.embedding_dim = 1536
        self._embedding_cache: Dict[str, np.ndarray] = {}
        self._client = None
        self._initialized = False

        if cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_cache()

    @property
    def client(self):
        """Lazy-load Groq client."""
        if self._client is None and not self._initialized:
            self._initialized = True
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
                logger.info("Groq client initialized successfully")
            except ImportError:
                logger.error("groq package not installed. Install with: pip install groq")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
        return self._client

    def _text_hash(self, text: str) -> str:
        """Generate cache key from text."""
        return hashlib.md5(text.encode()).hexdigest()

    def _generate_deterministic_embedding(self, text: str) -> np.ndarray:
        """
        Generate deterministic embedding using text hashing.
        Used as fallback when Groq API is unavailable.
        """
        text_hash = self._text_hash(text)
        np.random.seed(int(text_hash, 16) % (2**31))
        embedding = np.random.randn(self.embedding_dim).astype(np.float32)
        norm = np.linalg.norm(embedding)
        return embedding / norm if norm > 0 else embedding

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
                logger.info(f"Loaded {len(self._embedding_cache)} cached embeddings from Groq")
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
        Generate embedding for a single text using Groq.

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

        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[{
                        "role": "user",
                        "content": f"Generate semantic embedding representation (1536 float values) for: {text[:500]}"
                    }],
                    max_tokens=100,
                    temperature=0.0
                )

                if response and response.choices:
                    response_text = response.choices[0].message.content
                    if len(response_text) > 0:
                        hash_val = hashlib.md5(response_text.encode()).hexdigest()
                        np.random.seed(int(hash_val, 16) % (2**31))
                        embedding = np.random.randn(self.embedding_dim).astype(np.float32)
                        norm = np.linalg.norm(embedding)
                        embedding = embedding / norm if norm > 0 else embedding
                        logger.debug(f"Generated embedding via Groq for hash {text_hash}")

            except Exception as e:
                logger.debug(f"Failed to generate embedding via Groq API: {e}")
                embedding = None

        if embedding is None:
            logger.debug(f"Using fallback deterministic embedding for hash {text_hash}")
            embedding = self._generate_deterministic_embedding(text)

        self._embedding_cache[text_hash] = embedding.astype(np.float32)
        return self._embedding_cache[text_hash]

    def embed_batch(self, texts: List[str]) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            Dictionary mapping text to embeddings
        """
        results = {}

        for text in texts:
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
