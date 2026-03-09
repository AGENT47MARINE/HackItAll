import sys
import os
import io
from pypdf import PdfReader

def debug_pdf(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    try:
        with open(file_path, "rb") as f:
            pdf_content = f.read()
        
        reader = PdfReader(io.BytesIO(pdf_content))
        text = ""
        print(f"Number of pages: {len(reader.pages)}")
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            print(f"--- Page {i+1} ({len(page_text)} chars) ---")
            print(page_text[:500] + "...")
            text += page_text + "\n"
        
        print(f"Total extracted text length: {len(text)}")
    except Exception as e:
        print(f"Failed to read PDF: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_pdf(sys.argv[1])
    else:
        print("Usage: python debug_pdf.py <path_to_pdf>")
