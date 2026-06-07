from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PipelinePaths:
    integration_root: Path
    candidate_profiles_file: Path
    profile_dir: Path
    job_links_file: Path
    jd_catalog_file: Path
    match_results_file: Path
    email_dispatch_file: Path
    summary_file: Path


def build_paths(
    integration_root: Path,
    candidate_profiles_file: Path,
    profile_dir: Path,
) -> PipelinePaths:
    output_dir = integration_root / "output"
    data_dir = integration_root / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    profile_dir.mkdir(parents=True, exist_ok=True)

    return PipelinePaths(
        integration_root=integration_root,
        candidate_profiles_file=candidate_profiles_file,
        profile_dir=profile_dir,
        job_links_file=output_dir / "job_links.xlsx",
        jd_catalog_file=output_dir / "jd_catalog.csv",
        match_results_file=output_dir / "shortlisted_profiles.csv",
        email_dispatch_file=output_dir / "email_dispatch.csv",
        summary_file=output_dir / "pipeline_summary.json",
    )


def default_candidate_profiles_file(integration_root: Path) -> Path:
    return integration_root / "output" / "candidate_profiles.xlsx"


def default_profile_dir(integration_root: Path) -> Path:
    return integration_root / "output" / "naukri_browser_profile"
