from __future__ import annotations

import importlib
import re
import sys
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd


def _clean_text(value: str) -> str:
    value = value or ""
    value = re.sub(r"\s+", " ", str(value)).strip()
    return value


def _fallback_job(row: pd.Series) -> dict:
    title = _clean_text(str(row.get("Job Title", ""))) or "Unknown Role"
    technology = _clean_text(str(row.get("Technology", "")))
    posted = _clean_text(str(row.get("Posted", "")))
    company = _clean_text(str(row.get("Company", "")))

    description_parts = [
        f"Role: {title}",
        f"Technology: {technology}" if technology else "",
        f"Company: {company}" if company else "",
        f"Posted: {posted}" if posted else "",
        f"Source: {_clean_text(str(row.get('Job Link', '')))}",
    ]
    description = " | ".join(part for part in description_parts if part)

    skills = []
    for token in re.split(r"[,/|]", technology):
        skill = _clean_text(token)
        if skill:
            skills.append(skill)

    return {
        "role": title,
        "experience": "",
        "skills": skills,
        "description": description,
        "source": "fallback",
    }


def _simple_load_url_text(url: str) -> tuple[str, str]:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=20) as response:
        raw_html = response.read().decode("utf-8", errors="ignore")
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = unescape(text)
    text = _clean_text(text)
    return text, "stdlib-fallback"


def _identity_limit(text: str) -> str:
    return _clean_text(text)[:4000]


def _load_project_job_generator(job_generator_dir: Path):
    job_generator_dir = job_generator_dir.resolve()
    if str(job_generator_dir) not in sys.path:
        sys.path.insert(0, str(job_generator_dir))

    chain_cls = None
    load_url_text = _simple_load_url_text
    limit_text_for_llm = _identity_limit
    default_headers = {"User-Agent": "Mozilla/5.0"}

    try:
        utils_module = importlib.import_module("app.utils")
        load_url_text = utils_module.load_url_text
        limit_text_for_llm = utils_module.limit_text_for_llm
        default_headers = utils_module.DEFAULT_WEB_HEADERS
    except Exception:
        pass

    try:
        chains_module = importlib.import_module("app.chains")
        chain_cls = chains_module.Chain
    except Exception:
        chain_cls = None

    return chain_cls, load_url_text, limit_text_for_llm, default_headers


def generate_jd_catalog(job_links_df: pd.DataFrame, job_generator_dir: Path, max_rows: int | None = None) -> pd.DataFrame:
    rows = job_links_df if max_rows is None else job_links_df.iloc[:max_rows]

    chain_cls, load_url_text, limit_text_for_llm, default_headers = _load_project_job_generator(job_generator_dir)

    chain = None
    if chain_cls is not None:
        try:
            chain = chain_cls()
        except Exception:
            chain = None

    records: list[dict] = []

    for idx, row in rows.iterrows():
        job_link = _clean_text(str(row.get("Job Link", "")))
        base = {
            "row_num": int(idx) + 1,
            "job_link": job_link,
            "job_title": _clean_text(str(row.get("Job Title", ""))),
            "technology": _clean_text(str(row.get("Technology", ""))),
            "company": _clean_text(str(row.get("Company", ""))),
            "posted": _clean_text(str(row.get("Posted", ""))),
        }

        if not job_link.startswith(("http://", "https://")):
            fallback = _fallback_job(row)
            records.append({**base, **fallback})
            continue

        try:
            raw, source = load_url_text(job_link, min_chars=50, headers=default_headers)
            raw = limit_text_for_llm(raw)

            if not chain or len(_clean_text(raw)) < 50:
                fallback = _fallback_job(row)
                records.append({**base, **fallback, "source": source or fallback["source"]})
                continue

            jobs = chain.extract_jobs(raw)
            if not jobs:
                fallback = _fallback_job(row)
                records.append({**base, **fallback, "source": "llm-empty"})
                continue

            job = jobs[0]
            role = _clean_text(str(job.get("role", ""))) or base["job_title"] or "Unknown Role"
            experience = _clean_text(str(job.get("experience", "")))
            description = _clean_text(str(job.get("description", "")))
            skills = job.get("skills", [])
            if isinstance(skills, str):
                skills = [skills]
            skills = [_clean_text(str(skill)) for skill in skills if _clean_text(str(skill))]

            records.append(
                {
                    **base,
                    "role": role,
                    "experience": experience,
                    "skills": skills,
                    "description": description,
                    "source": "llm",
                }
            )
        except Exception:
            fallback = _fallback_job(row)
            records.append({**base, **fallback})

    return pd.DataFrame(records)
