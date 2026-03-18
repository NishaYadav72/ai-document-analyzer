from PyPDF2 import PdfReader
import pandas as pd
import pytesseract
from PIL import Image
import os
import re

# ---------------- TESSERACT CONFIG ----------------
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


# ---------------- PDF READER ----------------
def read_pdf(file_path):
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    # OCR fallback (scanned PDF)
    if text.strip() == "":
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(file_path)
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        except:
            text = "OCR not available on server."

    return {"pages": total_pages, "text": text}


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
        img = img.convert("L")
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return f"Image processing error: {str(e)}"


# ---------------- GENERIC LINE MATCH ----------------
def extract_relevant_lines(prompt, text, max_lines=5):
    lines = text.split("\n")
    prompt_words = prompt.lower().split()
    matched_lines = []

    for line in lines:
        line_lower = line.lower()

        if any(word in line_lower for word in prompt_words):
            matched_lines.append(line.strip())

        elif re.search(r'\d+', line) and any(word in line_lower for word in prompt_words):
            matched_lines.append(line.strip())

    return "\n".join(matched_lines[:max_lines]) if matched_lines else ""


def clean_text(text):
    # Multiple spaces remove
    text = re.sub(r'\s+', ' ', text)

    # Headings ke pehle newline add karo (IMPORTANT 🔥)
    headings = ["EXPERIENCE", "PROJECT", "SKILLS", "ACHIEVEMENTS", "OBJECTIVE"]

    for h in headings:
        text = text.replace(h, f"\n{h}\n")

    # Bullet points ke liye newline
    text = text.replace("•", "\n•")

    return text

# ---------------- SMART SECTION EXTRACTOR ----------------
def extract_section_strict(text, section_name):
    lines = text.split("\n")

    result = []
    capture = False

    for line in lines:
        clean_line = line.strip()
        line_upper = clean_line.upper()

        # ✅ EXACT HEADING MATCH (important)
        if line_upper == section_name.upper():
            capture = True
            continue

        # ✅ STOP when next heading comes (ALL CAPS)
        if capture and line_upper.isupper() and len(clean_line.split()) <= 3:
            break

        if capture:
            if clean_line:
                result.append(clean_line)

    return "\n".join(result).strip()


def extract_experience_smart(text):
    lines = text.split("\n")
    result = []

    for line in lines:
        line_lower = line.lower()

        # ❌ skip education type lines
        if any(word in line_lower for word in ["bca", "intermediate", "matriculation", "school", "college"]):
            continue

        # ❌ skip project headings
        if "tools & technologies" in line_lower:
            continue

        # ✅ pick only real experience lines
        if any(word in line_lower for word in [
            "worked", "developed", "experience", "project", "application", "system"
        ]):
            result.append(line.strip())

    return "\n".join(result[:6])  # limit

# ---------------- MAIN SMART EXTRACT FUNCTION ----------------
def smart_extract(prompt, text):
    text = clean_text(text)

    prompt_lower = prompt.lower()

    # EXPERIENCE (🔥 NEW SMART)
    if "experience" in prompt_lower:
        result = extract_experience_smart(text)
        if result:
            return result

    # PROJECT
    elif "project" in prompt_lower:
        return extract_relevant_lines(prompt, text)

    # NAME
    elif "name" in prompt_lower:
        return text.split("\n")[0]

    return extract_relevant_lines(prompt, text) or "Answer not found"