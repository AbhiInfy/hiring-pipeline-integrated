import pdfplumber
from docx import Document


def extract_pdf_text(uploaded_file):
    """Extract text from a PDF file."""

    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text.strip()


def extract_docx_text(uploaded_file):
    """Extract text from a DOCX file."""

    document = Document(uploaded_file)

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    )

    return text.strip()


def extract_resume_text(uploaded_file):
    """
    Extract text from uploaded resume.

    Returns:
        {
            success,
            text,
            error
        }
    """

    if uploaded_file is None:
        return {
            "success": False,
            "text": "",
            "error": "No resume uploaded."
        }

    try:

        filename = uploaded_file.name.lower()

        if filename.endswith(".pdf"):
            resume_text = extract_pdf_text(uploaded_file)

        elif filename.endswith(".docx"):
            resume_text = extract_docx_text(uploaded_file)

        else:
            return {
                "success": False,
                "text": "",
                "error": "Unsupported file format."
            }

        return {
            "success": True,
            "text": resume_text,
            "error": None
        }

    except Exception as e:

        return {
            "success": False,
            "text": "",
            "error": str(e)
        }