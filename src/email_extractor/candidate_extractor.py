"""
Email Candidate Extractor for Hiring Pipeline
Extracts candidate information from emails and CV attachments
"""

import os
import re
import email
import imaplib
import pandas as pd
from email.header import decode_header
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from io import BytesIO

# PDF and DOCX extraction
try:
    import PyPDF2
    import docx2txt
    from bs4 import BeautifulSoup
    EXTRACTION_AVAILABLE = True
except ImportError:
    EXTRACTION_AVAILABLE = False
    print("⚠️ Warning: PyPDF2 or docx2txt not installed. PDF/DOCX extraction disabled.")
    print("   Install with: pip install PyPDF2 docx2txt")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EmailCandidateExtractor:
    """Extracts candidate information from emails and saves to pipeline format"""
    
    def __init__(self, output_excel_path: str = "output/candidate_profiles.xlsx"):
        self.output_excel_path = Path(output_excel_path)
        self.output_excel_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Email configuration from environment
        self.email_user = os.getenv('IMAP_EMAIL') or os.getenv('SENDER_EMAIL')
        self.email_password = os.getenv('IMAP_PASSWORD') or os.getenv('SENDER_PASSWORD')
        self.imap_server = os.getenv('IMAP_SERVER', 'imap.gmail.com')
        
        if not self.email_user or not self.email_password:
            logger.warning("Email credentials not found in .env file")
        
        # Extraction patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+91[-.\s]?)?[6-9]\d{9}'
        
        # Technical skills keywords (customize for your needs)
        self.skills_keywords = [
            'oracle fusion', 'fusion financials', 'fusion hcm', 'fusion scm',
            'oracle cloud', 'oic', 'otbi', 'oracle ebs', 'python', 'java', 
            'sql', 'plsql', 'react', 'angular', 'node.js', 'aws', 'docker',
            'kubernetes', 'mongodb', 'postgresql', 'git', 'jenkins'
        ]
    
    def connect_imap(self):
        """Connect to email server via IMAP"""
        if not self.email_user or not self.email_password:
            logger.error("Email credentials not configured")
            return None
            
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_user, self.email_password)
            logger.info(f"✅ Connected to {self.imap_server}")
            return mail
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return None
    
    def fetch_recent_emails(self, hours_back: int = 24, folder: str = 'INBOX') -> List:
        """Fetch emails from last N hours"""
        mail = self.connect_imap()
        if not mail:
            return []
        
        try:
            mail.select(folder)
            since_date = (datetime.now() - timedelta(hours=hours_back)).strftime("%d-%b-%Y")
            result, message_ids = mail.search(None, f'(SINCE "{since_date}")')
            
            if result != 'OK':
                logger.info("No emails found in date range")
                return []
            
            email_ids = message_ids[0].split()
            logger.info(f"📧 Found {len(email_ids)} emails since {since_date}")
            
            emails = []
            for num in email_ids:
                result, msg_data = mail.fetch(num, '(RFC822)')
                if result == 'OK':
                    emails.append(email.message_from_bytes(msg_data[0][1]))
                    
            mail.close()
            mail.logout()
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def extract_text_from_attachment(self, part) -> Optional[str]:
        """Extract text from PDF, DOCX, or TXT attachments"""
        filename = part.get_filename()
        if not filename or not EXTRACTION_AVAILABLE:
            return None
            
        text = ""
        try:
            if filename.lower().endswith('.pdf'):
                pdf_file = BytesIO(part.get_payload(decode=True))
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
                logger.info(f"📄 Extracted from PDF: {filename}")
                    
            elif filename.lower().endswith('.docx'):
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
                    tmp.write(part.get_payload(decode=True))
                    tmp_path = tmp.name
                text = docx2txt.process(tmp_path)
                os.unlink(tmp_path)
                logger.info(f"📄 Extracted from DOCX: {filename}")
                
            elif filename.lower().endswith('.txt'):
                text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                logger.info(f"📄 Extracted from TXT: {filename}")
                
            return text[:5000]  # Limit text length
            
        except Exception as e:
            logger.error(f"Error extracting from {filename}: {e}")
            return None
    
    def extract_email_body(self, msg) -> str:
        """Extract text body from email"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" in content_disposition:
                    continue
                    
                if content_type == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body += part.get_payload()
                elif content_type == "text/html":
                    try:
                        html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        soup = BeautifulSoup(html, 'html.parser')
                        body += soup.get_text()
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = msg.get_payload()
                
        return body[:10000]  # Limit body length
    
    def extract_candidate_info(self, msg) -> Optional[Dict]:
        """Extract candidate information from an email"""
        try:
            # Get subject and sender
            subject = decode_header(msg.get("Subject", ""))[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode('utf-8', errors='ignore')
            sender = msg.get("From", "")
            
            logger.info(f"Processing: {subject[:50]}...")
            
            # Extract content
            body = self.extract_email_body(msg)
            attachment_text = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_disposition() == "attachment":
                        text = self.extract_text_from_attachment(part)
                        if text:
                            attachment_text += text + "\n"
            
            all_text = body + " " + attachment_text
            
            if not all_text.strip():
                return None
            
            # Extract email addresses
            emails = re.findall(self.email_pattern, sender + " " + all_text)
            if not emails:
                return None
                
            primary_email = emails[0].lower()
            
            # Extract name
            name = self._extract_name(primary_email, all_text, sender)
            
            # Extract skills
            skills = self._extract_skills(all_text)
            
            # Extract notice period
            notice_period = self._extract_notice_period(all_text)
            
            # Extract phone
            phone = self._extract_phone(all_text)
            
            return {
                'candidate_name': name,
                'skills': skills,
                'email': primary_email,
                'notice_period_days': notice_period,
                'phone': phone,
                'source_email': sender,
                'subject': subject[:100],
                'extracted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            return None
    
    def _extract_name(self, email_addr: str, text: str, sender: str) -> str:
        """Extract candidate name from various sources"""
        # Try from email address
        name_part = email_addr.split('@')[0]
        name_part = re.sub(r'[0-9._-]+', ' ', name_part)
        name = name_part.strip().title()
        
        # Try to extract from "Name:" field
        name_patterns = [
            r'(?:name|candidate|applicant)\s*[:|]\s*([A-Za-z\s]+)',
            r'(?:i am|my name is)\s+([A-Za-z\s]+?)(?:\.|$)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text[:500], re.I)
            if match:
                extracted = match.group(1).strip()
                if len(extracted.split()) >= 2:
                    name = extracted
                    break
        
        # Try from sender field (e.g., "John Doe <john@example.com>")
        sender_match = re.search(r'([A-Za-z\s]+)\s*<', sender)
        if sender_match and len(sender_match.group(1).split()) >= 2:
            name = sender_match.group(1).strip()
        
        return name if name else "Unknown Candidate"
    
    def _extract_skills(self, text: str) -> str:
        """Extract technical skills from text"""
        if not text:
            return "Not specified"
            
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.skills_keywords:
            if skill in text_lower:
                found_skills.add(skill)
        
        # Also look for skills section
        skill_section_match = re.search(r'(?:skills|technical skills|core competencies)\s*[:|]\s*([^\n]+)', text_lower)
        if skill_section_match:
            section_skills = skill_section_match.group(1)
            for skill in self.skills_keywords:
                if skill in section_skills:
                    found_skills.add(skill)
        
        return ', '.join(sorted(found_skills)) if found_skills else "Not specified"
    
    def _extract_notice_period(self, text: str) -> str:
        """Extract notice period in days"""
        if not text:
            return "30"
            
        text_lower = text.lower()
        patterns = [
            (r'notice\s*period\s*[:|]\s*(\d+)\s*days?', 'days'),
            (r'joining\s*[:|]\s*(\d+)\s*days?', 'days'),
            (r'(?:can join|available to join)\s+(?:in\s+)?(\d+)\s*days?', 'days'),
            (r'notice\s*period\s*[:|]\s*(immediate)', 'immediate'),
        ]
        
        for pattern, _ in patterns:
            match = re.search(pattern, text_lower, re.I)
            if match:
                if 'immediate' in match.group(0):
                    return "0"
                days = match.group(1) if match.groups() else None
                if days and days.isdigit():
                    return days
        
        # Check for "Immediate" or "Immediately"
        if re.search(r'\bimmediate(?:ly)?\b', text_lower):
            return "0"
                    
        return "30"
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        if not text:
            return ""
        
        phones = re.findall(self.phone_pattern, text)
        return phones[0] if phones else ""
    
    def load_existing_candidates(self) -> pd.DataFrame:
        """Load existing candidates from Excel"""
        if self.output_excel_path.exists():
            try:
                df = pd.read_excel(self.output_excel_path)
                required_cols = ['candidate_name', 'skills', 'email', 'notice_period_days']
                for col in required_cols:
                    if col not in df.columns:
                        df[col] = ''
                return df
            except Exception as e:
                logger.error(f"Error loading existing file: {e}")
        
        return pd.DataFrame(columns=['candidate_name', 'skills', 'email', 'notice_period_days'])
    
    def save_candidates(self, candidates: List[Dict]) -> int:
        """Save new candidates to Excel, avoiding duplicates"""
        if not candidates:
            return 0
        
        existing_df = self.load_existing_candidates()
        
        # Filter duplicates by email
        existing_emails = set(existing_df['email'].str.lower()) if not existing_df.empty else set()
        
        new_candidates = []
        for cand in candidates:
            if cand['email'].lower() not in existing_emails:
                # Keep only pipeline-required columns
                clean_cand = {
                    'candidate_name': cand['candidate_name'],
                    'skills': cand['skills'],
                    'email': cand['email'],
                    'notice_period_days': cand['notice_period_days']
                }
                new_candidates.append(clean_cand)
                existing_emails.add(cand['email'].lower())
        
        if not new_candidates:
            logger.info("No new candidates to add")
            return 0
        
        # Combine and save
        new_df = pd.DataFrame(new_candidates)
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
        final_df.to_excel(self.output_excel_path, index=False)
        
        logger.info(f"💾 Saved {len(new_candidates)} new candidates")
        return len(new_candidates)
    
    def run_extraction(self, hours_back: int = 24, max_emails: int = 50) -> int:
        """Main extraction workflow"""
        print("\n" + "="*60)
        print("📧 EMAIL CANDIDATE EXTRACTION")
        print("="*60)
        print(f"Scanning emails from last {hours_back} hours...")
        
        # Fetch emails
        emails = self.fetch_recent_emails(hours_back)
        
        if not emails:
            print("No emails found to process")
            return 0
        
        # Extract from each email
        candidates = []
        for msg in emails[:max_emails]:
            candidate = self.extract_candidate_info(msg)
            if candidate:
                candidates.append(candidate)
                print(f"  ✓ Found: {candidate['candidate_name']} ({candidate['email']})")
        
        # Save to Excel
        saved_count = self.save_candidates(candidates)
        
        # Summary
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"📧 Emails processed: {min(len(emails), max_emails)}")
        print(f"👥 Candidates found: {len(candidates)}")
        print(f"✨ New candidates added: {saved_count}")
        print(f"📁 Output: {self.output_excel_path}")
        print("="*60)
        
        return saved_count


def extract_candidates_from_emails(hours_back: int = 24, max_emails: int = 50) -> int:
    """Convenience function for pipeline integration"""
    extractor = EmailCandidateExtractor()
    return extractor.run_extraction(hours_back=hours_back, max_emails=max_emails)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract candidates from emails")
    parser.add_argument("--hours", type=int, default=24, help="Hours back to scan")
    parser.add_argument("--max-emails", type=int, default=50, help="Max emails to process")
    args = parser.parse_args()
    
    extract_candidates_from_emails(hours_back=args.hours, max_emails=args.max_emails)