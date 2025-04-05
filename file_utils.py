from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_file(file):
    if file.filename.endswith(".pdf"):
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file.filename.endswith(".docx"):
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    else:
        return None