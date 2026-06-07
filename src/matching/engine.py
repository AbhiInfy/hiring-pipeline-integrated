from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd


@dataclass
class MatchConfig:
    top_k: int = 5
    min_score: float = 0.12


MATCH_OUTPUT_COLUMNS = [
    "row_num",
    "job_link",
    "role",
    "technology",
    "company",
    "candidate_name",
    "candidate_email",
    "candidate_skills",
    "notice_period_days",
    "match_score",
    "overlap_terms",
]


def _tokenize(text: str) -> set[str]:
    tokens = set(re.findall(r"[a-zA-Z0-9+#._-]+", str(text).lower()))
    stopwords = {
        "and", "the", "for", "with", "from", "into", "role", "job", "skills",
        "experience", "developer", "engineer", "consultant", "years", "year",
    }
    return {token for token in tokens if len(token) > 2 and token not in stopwords}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a.intersection(b)) / len(a.union(b))


def match_candidates_to_jd(jd_df: pd.DataFrame, candidate_df: pd.DataFrame, config: MatchConfig | None = None) -> pd.DataFrame:
    config = config or MatchConfig()
    matches: list[dict] = []

    candidate_rows = []
    for _, candidate in candidate_df.iterrows():
        candidate_tokens = _tokenize(candidate.get("skills", ""))
        candidate_rows.append((candidate, candidate_tokens))

    for _, jd in jd_df.iterrows():
        jd_skill_text = " ".join(jd.get("skills", []) if isinstance(jd.get("skills", []), list) else [str(jd.get("skills", ""))])
        jd_text = " ".join([
            str(jd.get("role", "")),
            jd_skill_text,
            str(jd.get("description", "")),
            str(jd.get("technology", "")),
        ])
        jd_tokens = _tokenize(jd_text)

        ranked = []
        for candidate, candidate_tokens in candidate_rows:
            score = _jaccard(jd_tokens, candidate_tokens)
            if score < config.min_score:
                continue

            overlap = sorted(jd_tokens.intersection(candidate_tokens))
            ranked.append(
                {
                    "row_num": int(jd.get("row_num", 0)),
                    "job_link": str(jd.get("job_link", "")),
                    "role": str(jd.get("role", "")),
                    "technology": str(jd.get("technology", "")),
                    "company": str(jd.get("company", "")),
                    "candidate_name": str(candidate.get("candidate_name", "")),
                    "candidate_email": str(candidate.get("email", "")),
                    "candidate_skills": str(candidate.get("skills", "")),
                    "notice_period_days": str(candidate.get("notice_period_days", "")),
                    "match_score": round(float(score), 4),
                    "overlap_terms": ", ".join(overlap[:12]),
                }
            )

        ranked.sort(key=lambda item: item["match_score"], reverse=True)
        matches.extend(ranked[: config.top_k])

    result = pd.DataFrame(matches, columns=MATCH_OUTPUT_COLUMNS)
    if not result.empty:
        result = result.sort_values(["row_num", "match_score"], ascending=[True, False]).reset_index(drop=True)
    return result
