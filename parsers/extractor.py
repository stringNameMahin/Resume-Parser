from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import docx
from io import BytesIO
from typing import Union

def extract_text_from_pdf(file_path: Union[str, bytes]):
    # Wrap bytes in BytesIO if needed
    if isinstance(file_path, bytes):
        file_io = BytesIO(file_path)
    else:
        file_io = file_path

    # Extract text using PyPDF2
    reader = PdfReader(file_io)
    full_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text.append(text)
    text_content = " ".join(full_text)

    # Extract links using PyMuPDF
    if isinstance(file_path, bytes):
        doc = fitz.open(stream=file_path, filetype="pdf")
    else:
        doc = fitz.open(file_path)
    all_links = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        links = page.get_links()
        for link in links:
            if 'uri' in link:
                all_links.append({
                    "page": page_num + 1,
                    "uri": link['uri']
                })

    return text_content, all_links

def extract_text_from_docx(file_path: Union[str, bytes]):
    # Wrap bytes in BytesIO if needed
    if isinstance(file_path, bytes):
        file_io = BytesIO(file_path)
    else:
        file_io = file_path

    doc = docx.Document(file_io)
    return " ".join([p.text for p in doc.paragraphs])
