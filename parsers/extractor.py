from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import docx

def extract_text_from_pdf(file_path):
    # Extract text using PyPDF2
    reader = PdfReader(file_path)
    full_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text.append(text)
    text_content = " ".join(full_text)

    # Extract links using PyMuPDF
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

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return " ".join([p.text for p in doc.paragraphs])
