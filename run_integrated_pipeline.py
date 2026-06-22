from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.candidate_db.repository import load_candidate_profiles
from src.config import build_paths, default_candidate_profiles_file, default_profile_dir
from src.email.service import EmailDispatchConfig, dispatch_shortlist_emails
from src.env_loader import load_project_env
from src.ingest.naukri_scraper import scrape_job_links
from src.job_generator.jd_service import generate_jd_catalog as generate_jd_catalog_heuristic
from src.matching.engine import MatchConfig, match_candidates_to_jd

# Import email extractor
from src.email_extractor.candidate_extractor import extract_candidates_from_emails


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the 5-stage integrated hiring architecture pipeline.")
    parser.add_argument("--candidate-profiles-file", default="")
    parser.add_argument("--profile-dir", default="")
    parser.add_argument("--output", default="output/job_links.xlsx")

    # Email extraction arguments
    parser.add_argument("--extract-from-emails", action="store_true", 
                       help="Extract candidates from emails before running pipeline")
    parser.add_argument("--email-hours", type=int, default=24,
                       help="Hours back to scan emails (default: 24)")
    parser.add_argument("--max-emails", type=int, default=50,
                       help="Maximum emails to process (default: 50)")

    parser.add_argument("--keyword", default="Oracle Fusion Application")
    parser.add_argument("--pages", type=int, default=3)
    parser.add_argument("--max-age-hours", type=int, default=24)
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--login", action="store_true")
    parser.add_argument("--skip-contact-details", action="store_true")

    parser.add_argument("--rows", type=int, default=None)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--min-score", type=float, default=0.12)
    parser.add_argument("--default-email", default="chaturvedi.abhishek10@gmail.com")
    parser.add_argument("--email-provider", choices=["smtp", "sendgrid"], default="smtp")
    parser.add_argument("--send-emails", action="store_true")
    parser.add_argument("--notification-email", default="")
    return parser


def build_jd_catalog(job_links_df: pd.DataFrame, args) -> tuple[pd.DataFrame, str]:
    """Generate JD catalog using heuristic mode only."""
    return generate_jd_catalog_heuristic(job_links_df, max_rows=args.rows), "heuristic"


def main() -> int:
    args = build_parser().parse_args()

    integration_root = Path(__file__).resolve().parent
    load_project_env(integration_root)
    candidate_profiles_file = (
        Path(args.candidate_profiles_file).resolve()
        if args.candidate_profiles_file
        else default_candidate_profiles_file(integration_root)
    )
    profile_dir = Path(args.profile_dir).resolve() if args.profile_dir else default_profile_dir(integration_root)

    paths = build_paths(
        integration_root=integration_root,
        candidate_profiles_file=candidate_profiles_file,
        profile_dir=profile_dir,
    )

    output_path = (integration_root / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    paths.job_links_file = output_path
    runtime_warnings: list[str] = []

    # Stage 0 - Extract candidates from emails
    if args.extract_from_emails:
        print("\n" + "="*60)
        print("[Stage 0/6] Email Candidate Extraction...")
        print("="*60)
        new_candidates = extract_candidates_from_emails(
            hours_back=args.email_hours, 
            max_emails=args.max_emails
        )
        if new_candidates > 0:
            print(f"✅ Added {new_candidates} new candidates to database")
        else:
            print("ℹ️ No new candidates found")
        print()

    print("[Stage 1/5] Job Generator (JD Generation)...")
    scrape_job_links(
        keyword=args.keyword,
        output_path=output_path,
        profile_dir=paths.profile_dir,
        pages=args.pages,
        max_age_hours=args.max_age_hours,
        delay=args.delay,
        login=args.login,
        skip_contact_details=args.skip_contact_details,
    )

    # Ensure downstream stages always have a recipient email fallback in the exported job file.
    try:
        links_df = pd.read_excel(output_path)
        if "Email" not in links_df.columns:
            links_df["Email"] = ""
        links_df["Email"] = links_df["Email"].fillna("").astype(str)
        links_df["Email"] = links_df["Email"].apply(
            lambda value: args.default_email if value.strip() in {"", "nan", "None"} else value.strip()
        )
        links_df.to_excel(output_path, index=False)
    except Exception as exc:
        print(f"WARNING: could not apply default email to job_links.xlsx: {exc}")

    print("[Stage 2/5] Candidate Database (Resume Search)...")
    candidate_profiles = load_candidate_profiles(paths.candidate_profiles_file)
    
    # Validate candidate data
    if candidate_profiles.empty:
        print("\n" + "="*60)
        print("❌ PIPELINE STOPPED: No Valid Candidate Data")
        print("="*60)
        print("The candidate profiles file could not be loaded or contains no valid data.")
        print(f"File: {paths.candidate_profiles_file}")
        print("\nPlease ensure your Excel file has:")
        print("  • Required columns: Candidate Name, Skills, Email ID, Notice Period (Days)")
        print("  • At least one row with candidate name and skills")
        print("  • File is not open in another program")
        print("\nOptions:")
        print("  1. Create the file manually with candidate data")
        print("  2. Run with --extract-from-emails to auto-populate from emails")
        print("\nAfter fixing the file, re-run the pipeline.")
        return 1

    print("[Stage 3/5] AI Matching Engine (Similarity Search)...")
    job_links_df = pd.read_excel(output_path)
    jd_catalog, jd_mode_used = build_jd_catalog(job_links_df, args)
    jd_catalog.to_csv(paths.jd_catalog_file, index=False)
    print(f"JD generation mode used: {jd_mode_used}")

    # Use Jaccard matching only
    matches = match_candidates_to_jd(
        jd_catalog,
        candidate_profiles,
        config=MatchConfig(top_k=args.top_k, min_score=args.min_score),
    )
    matching_mode_used = "jaccard"

    print(f"Matching mode used: {matching_mode_used}")
    print(f"Total matches found: {len(matches)}")
    matches.to_csv(paths.match_results_file, index=False)

    print("[Stage 4/5] Email Service (SMTP / SendGrid)...")
    dispatch_df = dispatch_shortlist_emails(
        matches_df=matches,
        jd_catalog_df=jd_catalog,
        output_file=paths.email_dispatch_file,
        config=EmailDispatchConfig(
            provider=args.email_provider,
            send_emails=args.send_emails,
            notification_email=args.notification_email,
        ),
    )

    sent_count = int((dispatch_df["status"] == "sent").sum()) if not dispatch_df.empty else 0
    failed_count = int((dispatch_df["status"] == "failed").sum()) if not dispatch_df.empty else 0
    dry_run_count = int((dispatch_df["status"] == "dry-run").sum()) if not dispatch_df.empty else 0

    print("[Stage 5/5] Recruiter Dashboard...")
    summary = {
        "total_jobs": int(jd_catalog.shape[0]),
        "total_candidates": int(candidate_profiles.shape[0]),
        "total_matches": int(matches.shape[0]),
        "emails_sent": sent_count,
        "emails_failed": failed_count,
        "emails_dry_run": dry_run_count,
        "used_jd_mode": jd_mode_used,
        "used_matching_mode": matching_mode_used,
        "email_extraction_enabled": args.extract_from_emails,
        "warnings": runtime_warnings,
        "job_links_file": str(paths.job_links_file),
        "jd_catalog_file": str(paths.jd_catalog_file),
        "candidate_profiles_file": str(paths.candidate_profiles_file),
        "shortlisted_profiles_file": str(paths.match_results_file),
        "email_dispatch_file": str(paths.email_dispatch_file),
    }
    paths.summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Integrated architecture pipeline completed successfully.")
    print(f"Job links: {paths.job_links_file}")
    print(f"JD catalog: {paths.jd_catalog_file}")
    print(f"Candidate profiles: {paths.candidate_profiles_file}")
    print(f"Shortlisted profiles: {paths.match_results_file}")
    print(f"Email dispatch: {paths.email_dispatch_file}")
    print(f"Summary: {paths.summary_file}")
    if runtime_warnings:
        print("Warnings:")
        for warning in runtime_warnings:
            print(f"- {warning}")
    print("To view dashboard: streamlit run src/dashboard/app.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())