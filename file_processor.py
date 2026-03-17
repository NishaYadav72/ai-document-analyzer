from PyPDF2 import PdfReader
import pandas as pd
from pdf2image import convert_from_path
import easyocr
import numpy as np
from PIL import Image

# initialize EasyOCR reader once
reader = easyocr.Reader(['en'], gpu=False)

def read_pdf(file_path):
    reader_pdf = PdfReader(file_path)
    total_pages = len(reader_pdf.pages)
    text = ""

    # Try normal text extraction first
    for page in reader_pdf.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    # If PDF has no embedded text (scanned), use EasyOCR
    if text.strip() == "":
        try:
            images = convert_from_path(file_path, dpi=300)
            for img in images:
                img_np = np.array(img)
                result = reader.readtext(img_np, detail=0)
                text += "\n".join(result) + "\n"
        except Exception as poppler_error:
            # Render pe poppler missing ho sakta hai
            text += "\n[Scanned PDF OCR is not supported on this deployment]\n"
            
    return {
        "pages": total_pages,
        "text": text
    }

def read_excel(file_path):
    df = pd.read_excel(file_path)
    return df.to_string()

def read_image(file_path):
    # For direct image OCR
    result = reader.readtext(file_path, detail=0)
    # join recognized text into string
    return "\n".join(result)

def extract_name(text):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "dob" in line.lower():
            for j in range(i - 1, -1, -1):
                name = lines[j].strip()
                if len(name.split()) >= 2:
                    if "father" not in name.lower():
                        return name
    return "Name not found"