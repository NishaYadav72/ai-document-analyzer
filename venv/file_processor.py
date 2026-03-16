from PyPDF2 import PdfReader
import pandas as pd
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def read_pdf(file_path):

    reader = PdfReader(file_path)

    total_pages = len(reader.pages)

    text = ""

    # Normal text extraction
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    # Agar scanned PDF ho to OCR use karo
    if text.strip() == "":
        images = convert_from_path(file_path, dpi=300)
        for img in images:
            text += pytesseract.image_to_string(img)

    return {
        "pages": total_pages,
        "text": text
    }


def read_excel(file_path):
    df = pd.read_excel(file_path)
    return df.to_string()


def read_image(file_path):

    img = Image.open(file_path)

    # grayscale conversion
    img = img.convert("L")

    # OCR text
    text = pytesseract.image_to_string(img)

    return text

def extract_name(text):

    lines = text.split("\n")

    for i, line in enumerate(lines):

        if "dob" in line.lower():

            # DOB ke upar ka name find karo
            for j in range(i-1, -1, -1):

                name = lines[j].strip()

                if len(name.split()) >= 2:

                    if "father" not in name.lower():
                        return name

    return "Name not found"