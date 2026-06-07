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
    return (value or "").strip()


def _build_subject(role: str, company: str) -> str:
    role_clean = _clean(role) or "Open Role"
    company_clean = _clean(company) or "Client"
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
    notice = _clean(value)
    if not notice:
        return "Immediate Joiner"
    lowered = notice.lower()
    if "immediate" in lowered:
        return "Immediate Joiner"
    return f"{notice} days"


def _build_candidate_lines(candidates: Iterable[dict]) -> str:
    candidate_rows = list(candidates)
    if not candidate_rows:
        return "- No strong candidates identified yet for this requirement."

    lines = []
    for candidate in candidate_rows[:3]:
        name = _clean(str(candidate.get("candidate_name", ""))) or "Candidate"
        skills = _clean(str(candidate.get("candidate_skills", ""))) or "Relevant Oracle Fusion skills"
        notice_period = _format_notice_period(str(candidate.get("notice_period_days", "")))
        lines.append(f"- {name} | {skills} | {notice_period}")

    return "\n".join(lines)


def _build_body(row_num: int, role: str, company: str, candidates: Iterable[dict]) -> str:
    role_text = _clean(role) or "L2 Application Support Oracle Fusion Financials"
    sender_name = _clean(os.getenv("MAIL_SENDER_NAME", "Abhishek"))
    sender_title = _clean(os.getenv("MAIL_SENDER_TITLE", "Business Development Executive, RSI"))
    candidate_lines = _build_candidate_lines(candidates)
    template = _load_email_template()

    _ = row_num, company  # Reserved for future placeholders.

    return template.format(
        role=role_text,
        candidate_lines=candidate_lines,
        sender_name=sender_name,
        sender_title=sender_title,
    )


def _smtp_send(recipient: str, subject: str, body: str) -> tuple[bool, str]:
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


def dispatch_shortlist_emails(
    matches_df: pd.DataFrame,
    jd_catalog_df: pd.DataFrame,
    output_file: Path,
    config: EmailDispatchConfig,
) -> pd.DataFrame:
    load_project_env(Path(__file__).resolve().parents[2])
    output_file.parent.mkdir(parents=True, exist_ok=True)

    recipient = _clean(config.notification_email) or _clean(os.getenv("PIPELINE_NOTIFICATION_EMAIL", ""))
    if not recipient:
        recipient = _clean(os.getenv("DEFAULT_FALLBACK_RECIPIENT", ""))

    dispatch_rows: list[dict] = []

    for _, jd in jd_catalog_df.iterrows():
        row_num = int(jd.get("row_num", 0))
        role = str(jd.get("role", ""))
        company = str(jd.get("company", ""))

        candidates = []
        if not matches_df.empty:
            candidates = matches_df[matches_df["row_num"] == row_num].head(5).to_dict("records")

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
                    "message": "Email generation only (send disabled)",
                    "subject": subject,
                }
            )
            continue

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

    dispatch_df = pd.DataFrame(
        dispatch_rows,
        columns=["row_num", "provider", "recipient", "status", "message", "subject"],
    )
    dispatch_df.to_csv(output_file, index=False)
    return dispatch_df
