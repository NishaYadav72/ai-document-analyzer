from PyPDF2 import PdfReader
import pandas as pd
import pytesseract
from PIL import Image
import os
import re

# ---------------- TESSERACT CONFIG ----------------
# Local me chale, server me fail ho to ignore kare
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


# ---------------- PDF READER ----------------
def read_pdf(file_path):

    reader = PdfReader(file_path)
    total_pages = len(reader.pages)

    text = ""

    # Normal text extraction
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    # Agar text nahi mila (scanned PDF)
    if text.strip() == "":
        try:
            text = "Scanned PDF detected. OCR not supported on server."
        except Exception as e:
            text = f"OCR Error: {str(e)}"

    return {
        "pages": total_pages,
        "text": text
    }


# ---------------- EXCEL READER ----------------
def read_excel(file_path):

    try:
        df = pd.read_excel(file_path)
        return df.to_string()

    except Exception as e:
        return f"Excel reading error: {str(e)}"


# ---------------- IMAGE READER ----------------
def read_image(file_path):

    try:
        img = Image.open(file_path)

        # grayscale conversion
        img = img.convert("L")

        try:
            # OCR try karo
            text = pytesseract.image_to_string(img)
        except:
            text = "OCR not available on server"

        return text

    except Exception as e:
        return f"Image processing error: {str(e)}"


# ---------------- EXPERIENCE EXTRACTION ----------------
def extract_experience(text):

    lines = text.split("\n")

    for line in lines:
        if "experience" in line.lower():
            return line

    return "Experience not found"


# ---------------- NAME EXTRACTION ----------------
def extract_name(text):

    lines = text.split("\n")

    for i, line in enumerate(lines):

        if "dob" in line.lower():

            # DOB ke upar ka name find karo
            for j in range(i - 1, -1, -1):

                name = lines[j].strip()

                if len(name.split()) >= 2:

                    if "father" not in name.lower():
                        return name

    return "Name not found"