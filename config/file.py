

import PyPDF2 
import tempfile
import os


def extract_text_from_bytes(contents):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(contents)
        temp_path = temp_file.name

    text = extract_text(temp_path)
    os.remove(temp_path)  # Geçici dosyayı sil
    return text

def extract_text(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        text = ""

        for i in range(num_pages):
            page = reader.pages[i]
            text += page.extract_text() + "\n"

        return text