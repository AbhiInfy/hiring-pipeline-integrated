import logging
import numpy as np
from typing import Optional, Dict, Tuple, Union
import pandas as pd

from src.matching.engine import (
    MatchConfig,
    _tokenize,
    _calculate_jaccard_similarity,
    MATCH_COLUMNS
)

logger = logging.getLogger(__name__)


class SemanticMatcher:
    """Semantic matching using embeddings with optional blending with token-based matching."""

    def __init__(
        self,
        embeddings_service,
        blend_ratio: float = 0.7,
        config: Optional[MatchConfig] = None
    ):
        """
        Initialize semantic matcher.

        Args:
            embeddings_service: Embeddings service instance (Groq, Sentence Transformers, or Hybrid)
            blend_ratio: Weight for semantic score (0.0-1.0). Final = semantic*blend + token*(1-blend)
            config: MatchConfig for thresholds and limits
        """
        self.embeddings_service = embeddings_service
        self.blend_ratio = max(0.0, min(1.0, blend_ratio))
        self.config = config or MatchConfig()

    def _prepare_jd_text(self, row: pd.Series) -> str:
        """Prepare JD text for embedding."""
        parts = []
        if pd.notna(row.get("role")):
            parts.append(str(row["role"]))
        if pd.notna(row.get("technology")):
            parts.append(str(row["technology"]))
        if pd.notna(row.get("skills")):
            skills = row["skills"]
            if isinstance(skills, list):
                parts.append(" ".join(skills))
            else:
                parts.append(str(skills))
        if pd.notna(row.get("description")):
            desc = str(row["description"])
            parts.append(desc[:500])

        return " ".join(parts)

    def _prepare_candidate_text(self, candidate_skills: str) -> str:
        """Prepare candidate text for embedding."""
        return str(candidate_skills) if pd.notna(candidate_skills) else ""

    def _calculate_skill_match_details(
        self,
        jd_skills: list,
        candidate_skills: str,
        overlap_terms: str = ""
    ) -> str:
        """
        Generate human-readable skill match details.

        Args:
            jd_skills: List of JD skills
            candidate_skills: Candidate skills string
            overlap_terms: Overlapping terms from token matching

        Returns:
            Formatted string with matched/missing skills
        """
        if not overlap_terms:
            return ""

        matched = overlap_terms.split(", ")
        missing = []

        if isinstance(jd_skills, list):
            for skill in jd_skills:
                if isinstance(skill, dict):
                    skill_name = skill.get("name", str(skill)).lower()
                else:
                    skill_name = str(skill).lower()

                if not any(skill_name in m.lower() or m.lower() in skill_name for m in matched):
                    missing.append(str(skill))

        details_parts = []
        if matched:
            details_parts.append(f"Matched: {', '.join(matched[:5])}")
        if missing:
            details_parts.append(f"Missing: {', '.join(missing[:3])}")

        return " | ".join(details_parts)

    def match_candidates_to_jd_semantic(
        self,
        jd_catalog: pd.DataFrame,
        candidates: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Match candidates to JDs using semantic similarity blended with token matching.

        Args:
            jd_catalog: DataFrame with job descriptions
            candidates: DataFrame with candidate profiles

        Returns:
            DataFrame with matches and scores
        """
        logger.info(f"Starting semantic matching for {len(jd_catalog)} JDs and {len(candidates)} candidates")

        matches = []

        for jd_idx, jd_row in jd_catalog.iterrows():
            jd_text = self._prepare_jd_text(jd_row)

            if not jd_text.strip():
                logger.warning(f"Empty JD text for row {jd_idx}")
                continue

            jd_embedding = self.embeddings_service.embed_text(jd_text)

            if jd_embedding is None:
                logger.warning(f"Failed to generate embedding for JD row {jd_idx}, skipping")
                continue

            jd_tokens = _tokenize(jd_text)

            candidate_matches = []

            for cand_idx, candidate in candidates.iterrows():
                candidate_skills = candidate.get("skills", "")
                candidate_text = self._prepare_candidate_text(candidate_skills)

                if not candidate_text.strip():
                    continue

                cand_embedding = self.embeddings_service.embed_text(candidate_text)

                if cand_embedding is None:
                    logger.debug(f"Failed to generate embedding for candidate {cand_idx}")
                    cand_embedding = np.zeros(self.embeddings_service.embedding_dim)

                semantic_score = self.embeddings_service.cosine_similarity(jd_embedding, cand_embedding)

                cand_tokens = _tokenize(candidate_text)
                token_score = _calculate_jaccard_similarity(jd_tokens, cand_tokens)

                final_score = (semantic_score * self.blend_ratio) + (token_score * (1 - self.blend_ratio))

                if final_score >= self.config.min_score:
                    overlap = sorted(jd_tokens.intersection(cand_tokens), key=str.lower)[:12]
                    overlap_terms = ", ".join(overlap) if overlap else ""

                    skill_details = self._calculate_skill_match_details(
                        jd_row.get("skills", []),
                        candidate_skills,
                        overlap_terms
                    )

                    candidate_matches.append({
                        "candidate_idx": cand_idx,
                        "candidate_name": candidate.get("candidate_name", "Unknown"),
                        "candidate_email": candidate.get("email", ""),
                        "candidate_skills": candidate_skills,
                        "notice_period_days": candidate.get("notice_period_days", ""),
                        "semantic_score": semantic_score,
                        "token_score": token_score,
                        "final_score": final_score,
                        "overlap_terms": overlap_terms,
                        "skill_match_details": skill_details,
                    })

            candidate_matches.sort(key=lambda x: x["final_score"], reverse=True)

            for rank, match in enumerate(candidate_matches[:self.config.top_k], 1):
                match_record = {
                    "row_num": jd_row.get("row_num", jd_idx),
                    "job_link": jd_row.get("job_link", ""),
                    "role": jd_row.get("role", jd_row.get("job_title", "")),
                    "technology": jd_row.get("technology", ""),
                    "company": jd_row.get("company", ""),
                    "candidate_name": match["candidate_name"],
                    "candidate_email": match["candidate_email"],
                    "candidate_skills": match["candidate_skills"],
                    "notice_period_days": match["notice_period_days"],
                    "token_score": match["token_score"],
                    "semantic_score": match["semantic_score"],
                    "final_score": match["final_score"],
                    "overlap_terms": match["overlap_terms"],
                    "skill_match_details": match["skill_match_details"],
                }
                matches.append(match_record)

        df_matches = pd.DataFrame(matches)

        if len(df_matches) > 0:
            df_matches = df_matches.sort_values(
                by=["row_num", "final_score"],
                ascending=[True, False]
            ).reset_index(drop=True)

        logger.info(f"Found {len(df_matches)} total matches across all JDs")
        return df_matches
