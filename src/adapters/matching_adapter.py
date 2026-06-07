from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

import pandas as pd

from ..matching.engine import MATCH_OUTPUT_COLUMNS


def _as_text(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"", "nan", "none", "null"}:
        return ""
    return text


def _parse_skills(value) -> list[str]:
    if isinstance(value, list):
        return [_as_text(item) for item in value if _as_text(item)]

    text = _as_text(value)
    if not text:
        return []

    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return [_as_text(item) for item in parsed if _as_text(item)]
        except Exception:
            pass

    return [_as_text(part) for part in text.replace("|", ",").split(",") if _as_text(part)]


def _fallback_build_match_queries(job: dict, source_text: str, max_queries: int = 8) -> list[str]:
    queries = []

    role = _as_text(job.get("role", ""))
    skills = _parse_skills(job.get("skills", []))
    description = _as_text(job.get("description", ""))

    if role:
        queries.append(role)

    queries.extend(skills[: max_queries // 2])

    for text in [description, source_text]:
        for token in text.replace("|", " ").replace(",", " ").split():
            token = _as_text(token)
            if len(token) >= 3 and token.lower() not in {"and", "for", "with", "the", "job", "role"}:
                queries.append(token)
            if len(queries) >= max_queries:
                break
        if len(queries) >= max_queries:
            break

    deduped = []
    seen = set()
    for query in queries:
        key = query.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(query)
        if len(deduped) >= max_queries:
            break

    return deduped


def _load_project_job_generator(job_generator_dir: Path):
    job_generator_dir = job_generator_dir.resolve()
    if str(job_generator_dir) not in sys.path:
        sys.path.insert(0, str(job_generator_dir))

    portfolio_module = importlib.import_module("app.portfolio")
    build_match_queries = _fallback_build_match_queries
    try:
        utils_module = importlib.import_module("app.utils")
        build_match_queries = utils_module.build_match_queries
    except Exception:
        pass

    return portfolio_module.Portfolio, build_match_queries


def match_candidates_to_jd_adapter(
    jd_df: pd.DataFrame,
    *,
    job_generator_dir: Path,
    top_k: int = 5,
    min_score: float = 0.12,
) -> pd.DataFrame:
    Portfolio, build_match_queries = _load_project_job_generator(job_generator_dir)

    portfolio_file = job_generator_dir / "app" / "resource" / "Resource Details Sample.xlsx"
    portfolio = Portfolio(file_path=str(portfolio_file))
    portfolio.load_portfolio()

    matches: list[dict] = []

    for _, jd in jd_df.iterrows():
        row_num = int(jd.get("row_num", 0))
        role = _as_text(jd.get("role", ""))
        technology = _as_text(jd.get("technology", ""))
        company = _as_text(jd.get("company", ""))
        description = _as_text(jd.get("description", ""))
        jd_skills = _parse_skills(jd.get("skills", []))

        job_payload = {
            "role": role,
            "skills": jd_skills,
            "description": description,
        }
        queries = build_match_queries(job_payload, description)
        if not queries:
            fallback_query = " ".join(part for part in [role, technology] if part)
            queries = [fallback_query] if fallback_query else []

        raw_matches = portfolio.query_links(queries)
        ranked: dict[str, dict] = {}

        for group in raw_matches:
            for candidate in group:
                candidate_name = _as_text(candidate.get("Candidate Name", ""))
                candidate_email = _as_text(candidate.get("Email ID", ""))
                candidate_skill = _as_text(candidate.get("Skill", ""))
                notice_period = _as_text(candidate.get("Notice Period (Days)", ""))
                overlap_terms = _as_text(candidate.get("Overlap Tokens", ""))

                score_raw = candidate.get("Match Score", 0)
                try:
                    score = float(score_raw)
                except Exception:
                    score = 0.0

                if score < min_score:
                    continue

                dedupe_key = f"{candidate_name}|{candidate_email}"
                mapped = {
                    "row_num": row_num,
                    "job_link": _as_text(jd.get("job_link", "")),
                    "role": role,
                    "technology": technology,
                    "company": company,
                    "candidate_name": candidate_name,
                    "candidate_email": candidate_email,
                    "candidate_skills": candidate_skill,
                    "notice_period_days": notice_period,
                    "match_score": round(score, 4),
                    "overlap_terms": overlap_terms,
                }

                existing = ranked.get(dedupe_key)
                if not existing or mapped["match_score"] > existing["match_score"]:
                    ranked[dedupe_key] = mapped

        row_matches = sorted(ranked.values(), key=lambda item: item["match_score"], reverse=True)[:top_k]
        matches.extend(row_matches)

    result = pd.DataFrame(matches, columns=MATCH_OUTPUT_COLUMNS)
    if not result.empty:
        result = result.sort_values(["row_num", "match_score"], ascending=[True, False]).reset_index(drop=True)
    return result
