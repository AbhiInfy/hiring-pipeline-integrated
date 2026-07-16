import logging
from typing import Optional, List, Dict, Tuple
import numpy as np
from pathlib import Path

from .groq_embeddings import GroqEmbeddingsService
from .sentence_transformers_embeddings import SentenceTransformersEmbeddingsService

logger = logging.getLogger(__name__)


class HybridEmbeddingsService:
    """Hybrid service: tries Groq (fast, free tier) first, falls back to Sentence Transformers (local)."""

    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[Path] = None, groq_priority: bool = True):
        """
        Initialize hybrid embeddings service.

        Args:
            api_key: Groq API key (Sentence Transformers doesn't need one)
            cache_dir: Directory to cache embeddings
            groq_priority: If True, try Groq first; if False, use Sentence Transformers first
        """
        self.cache_dir = cache_dir
        self.groq_priority = groq_priority
        self.embedding_dim = 1536  # Use larger dimension for consistency

        # Initialize both services
        self.groq_service = None
        self.sentence_service = None

        if groq_priority:
            try:
                self.groq_service = GroqEmbeddingsService(api_key=api_key, cache_dir=cache_dir)
                logger.info("Groq service initialized (primary)")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq service: {e}")

            try:
                self.sentence_service = SentenceTransformersEmbeddingsService(cache_dir=cache_dir)
                logger.info("Sentence Transformers service initialized (fallback)")
            except Exception as e:
                logger.warning(f"Failed to initialize Sentence Transformers service: {e}")
        else:
            try:
                self.sentence_service = SentenceTransformersEmbeddingsService(cache_dir=cache_dir)
                logger.info("Sentence Transformers service initialized (primary)")
            except Exception as e:
                logger.warning(f"Failed to initialize Sentence Transformers service: {e}")

            try:
                self.groq_service = GroqEmbeddingsService(api_key=api_key, cache_dir=cache_dir)
                logger.info("Groq service initialized (fallback)")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq service: {e}")

    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding using hybrid approach.

        Args:
            text: Text to embed

        Returns:
            1D numpy array of embeddings
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to embed_text")
            return None

        embedding = None

        # Try primary service first
        if self.groq_priority:
            if self.groq_service and self.groq_service.client:
                try:
                    logger.debug("Attempting embedding generation via Groq")
                    embedding = self.groq_service.embed_text(text)
                    if embedding is not None:
                        logger.debug("Successfully generated embedding via Groq")
                        return embedding
                except Exception as e:
                    logger.debug(f"Groq embedding failed: {e}, trying fallback")

            if self.sentence_service and self.sentence_service.model:
                try:
                    logger.debug("Attempting embedding generation via Sentence Transformers (fallback)")
                    embedding = self.sentence_service.embed_text(text)
                    if embedding is not None:
                        logger.debug("Successfully generated embedding via Sentence Transformers")
                        return embedding
                except Exception as e:
                    logger.debug(f"Sentence Transformers embedding failed: {e}")
        else:
            if self.sentence_service and self.sentence_service.model:
                try:
                    logger.debug("Attempting embedding generation via Sentence Transformers")
                    embedding = self.sentence_service.embed_text(text)
                    if embedding is not None:
                        logger.debug("Successfully generated embedding via Sentence Transformers")
                        return embedding
                except Exception as e:
                    logger.debug(f"Sentence Transformers embedding failed: {e}, trying fallback")

            if self.groq_service and self.groq_service.client:
                try:
                    logger.debug("Attempting embedding generation via Groq (fallback)")
                    embedding = self.groq_service.embed_text(text)
                    if embedding is not None:
                        logger.debug("Successfully generated embedding via Groq")
                        return embedding
                except Exception as e:
                    logger.debug(f"Groq embedding failed: {e}")

        logger.warning(f"Failed to generate embedding for text via both services")
        return None

    def embed_batch(self, texts: List[str]) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for multiple texts using hybrid approach.

        Args:
            texts: List of texts to embed

        Returns:
            Dictionary mapping text to embeddings
        """
        results = {}

        # Try primary service first
        if self.groq_priority:
            if self.groq_service and self.groq_service.client:
                try:
                    logger.info(f"Batch embedding {len(texts)} texts via Groq")
                    batch_results = self.groq_service.embed_batch(texts)
                    results.update(batch_results)
                    logger.info(f"Groq batch embedding succeeded for {len(batch_results)} texts")
                except Exception as e:
                    logger.warning(f"Groq batch embedding failed: {e}, using fallback")

            # Fall back to Sentence Transformers for any missing
            missing_texts = [t for t in texts if t not in results]
            if missing_texts and self.sentence_service and self.sentence_service.model:
                try:
                    logger.info(f"Batch embedding {len(missing_texts)} remaining texts via Sentence Transformers")
                    batch_results = self.sentence_service.embed_batch(missing_texts)
                    results.update(batch_results)
                    logger.info(f"Sentence Transformers batch embedding succeeded for {len(batch_results)} texts")
                except Exception as e:
                    logger.warning(f"Sentence Transformers batch embedding failed: {e}")
        else:
            if self.sentence_service and self.sentence_service.model:
                try:
                    logger.info(f"Batch embedding {len(texts)} texts via Sentence Transformers")
                    batch_results = self.sentence_service.embed_batch(texts)
                    results.update(batch_results)
                    logger.info(f"Sentence Transformers batch embedding succeeded for {len(batch_results)} texts")
                except Exception as e:
                    logger.warning(f"Sentence Transformers batch embedding failed: {e}, using fallback")

            # Fall back to Groq for any missing
            missing_texts = [t for t in texts if t not in results]
            if missing_texts and self.groq_service and self.groq_service.client:
                try:
                    logger.info(f"Batch embedding {len(missing_texts)} remaining texts via Groq")
                    batch_results = self.groq_service.embed_batch(missing_texts)
                    results.update(batch_results)
                    logger.info(f"Groq batch embedding succeeded for {len(batch_results)} texts")
                except Exception as e:
                    logger.warning(f"Groq batch embedding failed: {e}")

        if len(results) < len(texts):
            logger.warning(f"Only generated {len(results)}/{len(texts)} embeddings")

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
        """Clear cache in both services."""
        if self.groq_service:
            self.groq_service.clear_cache()
        if self.sentence_service:
            self.sentence_service.clear_cache()
        logger.info("Cache cleared in all services")

    def get_status(self) -> Dict[str, str]:
        """Get status of both services."""
        return {
            "groq_available": self.groq_service is not None and self.groq_service.client is not None,
            "sentence_transformers_available": self.sentence_service is not None and self.sentence_service.model is not None,
            "primary": "groq" if self.groq_priority else "sentence-transformers",
        }
