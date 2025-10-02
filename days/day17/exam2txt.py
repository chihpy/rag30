"""
convert exam_pdf2txt helper
"""
import os
import fitz  # pip install PyMuPDF

from utils import mkdir, txt_dump

SOURCE_DIR = os.path.join('data', 'source')
SOURCE_FILE_PATH = os.path.join(SOURCE_DIR, '114_針灸科學.pdf')
DEST_DIR = os.path.join('data', 'temp')
mkdir(DEST_DIR)

def pdf2txt_fitz(source_file_path):
    text = []
    with fitz.open(source_file_path) as doc:
        for page in doc:
            page_txt = page.get_text("text")
            text.append(page_txt)
    return "\n\n".join(text)

if __name__ == "__main__":
    file_path = SOURCE_FILE_PATH
    file_name = os.path.basename(file_path)
    txt_file_name = file_name.replace('.pdf', '.txt')
    save_file_path = os.path.join(DEST_DIR, txt_file_name)
    txt = pdf2txt_fitz(file_path)
    txt_dump(save_file_path, txt)