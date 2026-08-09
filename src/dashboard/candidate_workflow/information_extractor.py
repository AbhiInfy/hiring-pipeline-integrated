import re

def clean_resume_text(text):
    """Clean extracted resume text."""

    if not text:
        return ""

    # Remove PDF artifacts like (cid:123)
    text = re.sub(r"\(cid:\d+\)", " ", text)

    # Replace multiple spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Replace multiple blank lines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()
def extract_name(text):
    """Extract candidate name."""

    lines = text.split("\n")

    for line in lines[:10]:
        line = line.strip()

        if (
            len(line.split()) >= 2
            and len(line.split()) <= 4
            and "@" not in line
            and not any(char.isdigit() for char in line)
        ):
            return line

    return ""

def extract_email(text):
    """Extract email address."""

    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text,
    )

    if match:
        return match.group()

    return ""


def extract_phone(text):
    """Extract phone number."""

    patterns = [
        r"(\+91[\s-]?[6-9]\d{9})",
        r"([6-9]\d{9})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group()

    return ""


def extract_location(text):
    """Extract city/location."""

    locations = [
        "Delhi",
        "New Delhi",
        "Noida",
        "Gurgaon",
        "Gurugram",
        "Bangalore",
        "Bengaluru",
        "Hyderabad",
        "Pune",
        "Mumbai",
        "Chennai",
        "Kolkata",
        "Ahmedabad",
        "Jaipur",
        "Lucknow",
        "Dehradun",
        "Mohali",
        "Chandigarh",
        "Indore",
        "Nagpur",
    ]

    text_lower = text.lower()

    for city in locations:
        if city.lower() in text_lower:
            return city

    return ""


def extract_experience(text):
    """Extract years of experience."""

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group()

    return ""


def extract_role(text):
    """Extract probable job role."""

    roles = [
        "Oracle Fusion HCM Consultant",
        "Oracle Fusion Consultant",
        "Oracle HCM Consultant",
        "Oracle Technical Consultant",
        "Software Engineer",
        "Software Developer",
        "Python Developer",
        "Java Developer",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "Data Analyst",
        "Business Analyst",
        "Cloud Engineer",
        "DevOps Engineer",
        "QA Engineer",
        "Test Engineer",
        "Project Manager",
        "UI Developer",
        "React Developer",
        "Machine Learning Engineer",
        "AI Engineer",
    ]

    text_lower = text.lower()

    for role in roles:
        if role.lower() in text_lower:
            return role

    return ""


def extract_skills(text):
    """Extract skills from resume."""

    skills_master = [
        "Oracle Fusion",
        "Oracle HCM",
        "Core HR",
        "Absence Management",
        "Payroll",
        "Fast Formula",
        "SQL",
        "PL/SQL",
        "Python",
        "Java",
        "C++",
        "JavaScript",
        "React",
        "HTML",
        "CSS",
        "Git",
        "GitHub",
        "REST API",
        "Postman",
        "Streamlit",
        "FastAPI",
        "Docker",
        "Kubernetes",
        "AWS",
        "Azure",
        "Linux",
        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
        "Pandas",
        "NumPy",
        "Power BI",
        "Excel",
    ]

    found_skills = []

    text_lower = text.lower()

    for skill in skills_master:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return sorted(list(set(found_skills)))


def extract_candidate_information(text):
    """Extract structured candidate information."""

    cleaned_text = clean_resume_text(text)

    candidate_information = {
        "name": extract_name(cleaned_text),
        "email": extract_email(cleaned_text),
        "phone": extract_phone(cleaned_text),
        "role": extract_role(cleaned_text),
        "skills": extract_skills(cleaned_text),
        "experience": extract_experience(cleaned_text),
        "location": extract_location(cleaned_text),
    }

    return candidate_information