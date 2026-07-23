from __future__ import annotations

import re
from html import unescape
from urllib.request import Request, urlopen

import pandas as pd

def _clean(value: str) -> str:
    value = value or ""
    value = re.sub(r"\s+", " ", str(value)).strip()
    return value


def _extract_text_from_url(url: str) -> tuple[str, str]:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=25) as response:
        html = response.read().decode("utf-8", errors="ignore")
    text = re.sub(r"<[^>]+>", " ", html)
    text = _clean(unescape(text))
    return text[:5000], "html"


def _infer_skills(technology: str, description: str) -> list[str]:
    tokens = set()
    for source in [technology, description]:
        for part in re.split(r"[,/|]", str(source)):
            token = _clean(part)
            if len(token) >= 2:
                tokens.add(token)

    preferred = []
    for token in sorted(tokens):
        if re.search(r"oracle|fusion|hcm|scm|finance|cloud|python|java|sql|sap|ai|ml", token, re.IGNORECASE):
            preferred.append(token)

    if preferred:
        return preferred[:10]
    return sorted(tokens)[:10]


def _fallback_job(row: pd.Series) -> dict:
    title = _clean(str(row.get("Job Title", ""))) or "Unknown Role"
    technology = _clean(str(row.get("Technology", "")))
    posted = _clean(str(row.get("Posted", "")))
    company = _clean(str(row.get("Company", "")))

    description_parts = [
        f"Role: {title}",
        f"Technology: {technology}" if technology else "",
        f"Company: {company}" if company else "",
        f"Posted: {posted}" if posted else "",
        f"Source: {_clean(str(row.get('Job Link', '')))}",
    ]
    description = " | ".join(part for part in description_parts if part)

    return {
        "role": title,
        "experience": "",
        "skills": _infer_skills(technology, description),
        "description": description,
        "source": "fallback",
    }


def generate_jd_catalog(job_links_df: pd.DataFrame, max_rows: int | None = None) -> pd.DataFrame:
    rows = job_links_df if max_rows is None else job_links_df.iloc[:max_rows]
    records: list[dict] = []

    for idx, row in rows.iterrows():
        job_link = _clean(str(row.get("Job Link", "")))
        base = {
            "row_num": int(idx) + 1,
            "job_link": job_link,
            "job_title": _clean(str(row.get("Job Title", ""))),
            "technology": _clean(str(row.get("Technology", ""))),
            "company": _clean(str(row.get("Company", ""))),
            "posted": _clean(str(row.get("Posted", ""))),
        }

        if not job_link.startswith(("http://", "https://")):
            fallback = _fallback_job(row)
            records.append({**base, **fallback})
            continue

        try:
            raw_text, source = _extract_text_from_url(job_link)
            role = base["job_title"] or "Unknown Role"
            description = _clean(raw_text)[:1200]
            skills = _infer_skills(base["technology"], description)
            records.append(
                {
                    **base,
                    "role": role,
                    "experience": "",
                    "skills": skills,
                    "description": description,
                    "source": source,
                }
            )
        except Exception:
            fallback = _fallback_job(row)
            records.append({**base, **fallback})

    return pd.DataFrame(records)
