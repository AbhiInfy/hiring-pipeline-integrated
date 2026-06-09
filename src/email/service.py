from __future__ import annotations

import json
import os
import smtplib
from dataclasses import dataclass
from email.mime.text import MIMEText
from pathlib import Path
from typing import Iterable
from urllib.request import Request, urlopen

import pandas as pd

from ..env_loader import load_project_env


EMAIL_TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "oracle_fusion_financials_email_template.txt"


@dataclass
class EmailDispatchConfig:
    provider: str = "smtp"
    send_emails: bool = False
    notification_email: str = ""


def _clean(value: str) -> str:
    """Clean and normalize string values"""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"", "nan", "nat", "none", "null", "n/a", "na"}:
        return ""
    return text


def _clean_company_name(company: str) -> str:
    """
    Clean company name, handle missing, NaN, and invalid values.
    Returns a proper company name or default "Client" value.
    """
    # Handle None, NaN, or empty values
    if company is None or pd.isna(company):
        return "Client"
    
    # Convert to string and clean
    cleaned = str(company).strip()
    
    # Check for common invalid values
    invalid_values = {"", "nan", "NaN", "None", "null", "N/A", "n/a", "na", "-", "unknown", "not specified"}
    if cleaned.lower() in invalid_values or not cleaned:
        return "Client"
    
    # Remove any remaining NaN references
    cleaned = cleaned.replace("nan", "").replace("NaN", "").replace("None", "").strip()
    
    # If after cleaning it's empty, return default
    if not cleaned:
        return "Client"
    
    return cleaned


def _build_subject(role: str, company: str) -> str:
    """Build email subject with proper handling of missing values"""
    role_clean = _clean(role) or "Open Role"
    company_clean = _clean_company_name(company)
    return f"Shortlist Update: {role_clean} - {company_clean}"


def _load_email_template() -> str:
    if EMAIL_TEMPLATE_PATH.exists():
        return EMAIL_TEMPLATE_PATH.read_text(encoding="utf-8")

    # Fallback text keeps dispatch resilient if template file is missing.
    return (
        "Dear Hiring Manager,\n\n"
        "I came across the job description for an {role} role and was impressed by the requirements. "
        "At RSI, we specialize in providing tailored solutions for businesses, focusing on process optimization, "
        "cost reduction, and increased efficiency.\n\n"
        "Our team has extensive experience in implementing and supporting Oracle Fusion Financials, including "
        "GL/AP/AR, R2R & P2P, and Financial Reporting. We can help you streamline your financial processes, "
        "ensure seamless data migration, and integrate your ERP systems.\n\n"
        "Below are three strong candidates we have identified for this role:\n\n"
        "{candidate_lines}\n\n"
        "We would be delighted to discuss how RSI can support your Oracle Fusion Financials needs. "
        "Please let us know if you would like to schedule a call to explore further.\n\n"
        "Best regards,\n"
        "{sender_name}\n"
        "{sender_title}\n"
    )


def _format_notice_period(value: str) -> str:
    """Format notice period for display"""
    notice = _clean(value)
    if not notice:
        return "Immediate Joiner"
    lowered = notice.lower()
    if "immediate" in lowered:
        return "Immediate Joiner"
    return f"{notice} days"


def _build_candidate_lines(candidates: Iterable[dict]) -> str:
    """Build formatted candidate lines for email body"""
    candidate_rows = list(candidates)
    if not candidate_rows:
        return "- No strong candidates identified yet for this requirement."

    lines = []
    for candidate in candidate_rows[:3]:
        name = _clean(str(candidate.get("candidate_name", ""))) or "Candidate"
        skills = _clean(str(candidate.get("skills", ""))) or "Relevant Oracle Fusion skills"
        notice_period = _format_notice_period(str(candidate.get("notice_period_days", "")))
        lines.append(f"- {name} | {skills} | {notice_period}")

    return "\n".join(lines)


def _build_body(row_num: int, role: str, company: str, candidates: Iterable[dict]) -> str:
    """Build email body with cleaned company name"""
    role_text = _clean(role) or "L2 Application Support Oracle Fusion Financials"
    company_text = _clean_company_name(company)  # Use cleaned company name
    sender_name = _clean(os.getenv("MAIL_SENDER_NAME", "Abhishek"))
    sender_title = _clean(os.getenv("MAIL_SENDER_TITLE", "Business Development Executive, RSI"))
    candidate_lines = _build_candidate_lines(candidates)
    template = _load_email_template()

    # Use company_text for any future placeholders
    _ = row_num, company_text

    return template.format(
        role=role_text,
        candidate_lines=candidate_lines,
        sender_name=sender_name,
        sender_title=sender_title,
    )


def _smtp_send(recipient: str, subject: str, body: str) -> tuple[bool, str]:
    """Send email via SMTP"""
    server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    sender = _clean(os.getenv("SENDER_EMAIL", ""))
    password = _clean(os.getenv("SENDER_PASSWORD", "")).replace(" ", "")

    if not sender or not password:
        return False, "Missing SMTP credentials (SENDER_EMAIL/SENDER_PASSWORD)"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        if port == 465:
            with smtplib.SMTP_SSL(server, port, timeout=30) as client:
                client.login(sender, password)
                client.sendmail(sender, [recipient], msg.as_string())
        else:
            with smtplib.SMTP(server, port, timeout=30) as client:
                client.ehlo()
                if port == 587:
                    client.starttls()
                    client.ehlo()
                client.login(sender, password)
                client.sendmail(sender, [recipient], msg.as_string())
        return True, "Email sent via SMTP"
    except Exception as exc:
        return False, f"SMTP send failed: {exc}"


def _sendgrid_send(recipient: str, subject: str, body: str) -> tuple[bool, str]:
    """Send email via SendGrid API"""
    api_key = _clean(os.getenv("SENDGRID_API_KEY", ""))
    sender = _clean(os.getenv("SENDGRID_SENDER_EMAIL", os.getenv("SENDER_EMAIL", "")))
    if not api_key or not sender:
        return False, "Missing SendGrid configuration (SENDGRID_API_KEY/SENDGRID_SENDER_EMAIL)"

    payload = {
        "personalizations": [{"to": [{"email": recipient}]}],
        "from": {"email": sender},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
    }

    request = Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            status = getattr(response, "status", 202)
            if 200 <= status < 300:
                return True, "Email sent via SendGrid"
            return False, f"SendGrid responded with status {status}"
    except Exception as exc:
        return False, f"SendGrid send failed: {exc}"


def filter_jobs_with_matches(matches_df: pd.DataFrame, jd_catalog_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter JD catalog to only include jobs that have at least one matching candidate.
    Returns empty DataFrame if no jobs have matches.
    """
    if matches_df is None or matches_df.empty:
        print("\n⚠️ No matching candidates found. No jobs qualify for email dispatch.")
        return pd.DataFrame()
    
    # Check if row_num column exists
    if "row_num" not in matches_df.columns:
        print("\n⚠️ Warning: 'row_num' column not found in matches. Cannot filter jobs.")
        print("   Will attempt to send emails for all jobs.")
        return jd_catalog_df
    
    # Get unique row_num values from matches (jobs with at least one candidate)
    job_rows_with_matches = set(matches_df["row_num"].unique())
    
    # Filter JD catalog to only jobs that have matches
    filtered_jd_catalog = jd_catalog_df[jd_catalog_df["row_num"].isin(job_rows_with_matches)].copy()
    
    total_jobs = len(jd_catalog_df)
    jobs_with_matches = len(filtered_jd_catalog)
    jobs_without_matches = total_jobs - jobs_with_matches
    
    print(f"\n{'='*60}")
    print("📧 EMAIL DISPATCH FILTER")
    print(f"{'='*60}")
    print(f"Total jobs in catalog:     {total_jobs}")
    print(f"Jobs with matching candidates: {jobs_with_matches}")
    print(f"Jobs without any matches:  {jobs_without_matches}")
    
    if jobs_without_matches > 0:
        print(f"\n✅ Will send emails only for {jobs_with_matches} job(s) that have candidates.")
        print(f"❌ Skipping {jobs_without_matches} job(s) with no matching candidates.")
    
    if jobs_with_matches == 0:
        print("\n🚫 NO EMAILS WILL BE SENT - No jobs have matching candidates.")
    
    return filtered_jd_catalog


def dispatch_shortlist_emails(
    matches_df: pd.DataFrame,
    jd_catalog_df: pd.DataFrame,
    output_file: Path,
    config: EmailDispatchConfig,
) -> pd.DataFrame:
    """
    Dispatch emails for jobs with matching candidates.
    Handles missing company names gracefully.
    """
    load_project_env(Path(__file__).resolve().parents[2])
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Safety check for empty matches
    if matches_df is None or matches_df.empty:
        print("\n" + "="*60)
        print("❌ EMAIL DISPATCH SKIPPED")
        print("="*60)
        print("Reason: No matches found (empty matches DataFrame).")
        print("This usually means:")
        print("  • No candidate profiles were loaded")
        print("  • Candidate file is empty or has wrong columns")
        print("  • No candidates matched any jobs")
        print("\nNo emails will be sent.")
        
        empty_df = pd.DataFrame(columns=["row_num", "provider", "recipient", "status", "message", "subject"])
        empty_df.to_csv(output_file, index=False)
        return empty_df
    
    # Filter to only jobs with matching candidates
    filtered_jd_catalog = filter_jobs_with_matches(matches_df, jd_catalog_df)
    
    # If no jobs have matches, return empty
    if filtered_jd_catalog.empty:
        print("\n" + "="*60)
        print("❌ EMAIL DISPATCH SKIPPED")
        print("="*60)
        print("Reason: No jobs found with matching candidates.")
        print("No emails will be sent.")
        
        empty_df = pd.DataFrame(columns=["row_num", "provider", "recipient", "status", "message", "subject"])
        empty_df.to_csv(output_file, index=False)
        return empty_df

    # Get recipient email
    recipient = _clean(config.notification_email) or _clean(os.getenv("PIPELINE_NOTIFICATION_EMAIL", ""))
    if not recipient:
        recipient = _clean(os.getenv("DEFAULT_FALLBACK_RECIPIENT", ""))

    dispatch_rows: list[dict] = []

    # Iterate over filtered catalog
    for _, jd in filtered_jd_catalog.iterrows():
        row_num = int(jd.get("row_num", 0))
        role = str(jd.get("role", ""))
        company = str(jd.get("company", ""))

        # Get candidates for this specific job
        candidates = []
        if not matches_df.empty and "row_num" in matches_df.columns:
            candidates = matches_df[matches_df["row_num"] == row_num].head(5).to_dict("records")
        
        # Skip if no candidates for this job
        if not candidates:
            print(f"⚠️ Warning: Job '{role}' at {company} (row_num={row_num}) has no candidates. Skipping.")
            continue

        # Build subject and body (company name is cleaned inside these functions)
        subject = _build_subject(role, company)
        body = _build_body(row_num, role, company, candidates)

        if not recipient:
            dispatch_rows.append(
                {
                    "row_num": row_num,
                    "provider": config.provider,
                    "recipient": "",
                    "status": "skipped",
                    "message": "No notification recipient configured",
                    "subject": subject,
                }
            )
            continue

        if not config.send_emails:
            dispatch_rows.append(
                {
                    "row_num": row_num,
                    "provider": config.provider,
                    "recipient": recipient,
                    "status": "dry-run",
                    "message": f"Would send email for {len(candidates)} candidate(s) (send disabled)",
                    "subject": subject,
                }
            )
            continue

        # Send actual email
        provider = config.provider.lower().strip()
        if provider == "sendgrid":
            success, message = _sendgrid_send(recipient, subject, body)
        else:
            success, message = _smtp_send(recipient, subject, body)

        dispatch_rows.append(
            {
                "row_num": row_num,
                "provider": provider,
                "recipient": recipient,
                "status": "sent" if success else "failed",
                "message": message,
                "subject": subject,
            }
        )
    
    # Print summary
    if dispatch_rows:
        print(f"\n{'='*60}")
        print("📧 EMAIL DISPATCH SUMMARY")
        print(f"{'='*60}")
        print(f"Emails dispatched for {len(dispatch_rows)} job(s) with candidates")
        
        if not config.send_emails:
            print("⚠️ DRY-RUN MODE: No actual emails were sent")
            print(f"   Would have sent {len(dispatch_rows)} email(s)")
        elif config.send_emails:
            sent = sum(1 for r in dispatch_rows if r["status"] == "sent")
            failed = sum(1 for r in dispatch_rows if r["status"] == "failed")
            print(f"✅ Successfully sent: {sent}")
            print(f"❌ Failed: {failed}")
    else:
        print("\n✅ No emails to dispatch - all jobs lacked matching candidates")

    dispatch_df = pd.DataFrame(
        dispatch_rows,
        columns=["row_num", "provider", "recipient", "status", "message", "subject"],
    )
    dispatch_df.to_csv(output_file, index=False)
    return dispatch_df