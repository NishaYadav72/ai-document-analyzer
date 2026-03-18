from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import shutil
import os

from file_processor import read_pdf, read_excel, read_image
from llm_engine import ask_llm
from reportlab.pdfgen import canvas

app = FastAPI()

templates = Jinja2Templates(directory="templates")

os.makedirs("uploads", exist_ok=True)


# ---------------- HOME ----------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------- ANALYZE ----------------
@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request, file: UploadFile = File(...), prompt: str = Form(...)):

    file_location = f"uploads/{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    context = ""
    pages = 0

    # PDF
    if file.filename.endswith(".pdf"):
        data = read_pdf(file_location)
        context = data["text"]
        pages = data["pages"]

    # Excel
    elif file.filename.endswith(".xlsx"):
        context = read_excel(file_location)
        pages = 1

    # Image
    elif file.filename.endswith((".png", ".jpg", ".jpeg")):
        context = read_image(file_location)
        pages = 1

    print("DOCUMENT TEXT:", context)

    # ✅ SMART AI RESPONSE
    result = ask_llm(prompt, context)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "result": result,
            "pages": pages
        }
    )


# ---------------- PDF DOWNLOAD ----------------
@app.post("/download-pdf")
async def download_pdf(result: str = Form(...)):

    file_path = "result.pdf"

    c = canvas.Canvas(file_path)
    c.setFont("Helvetica", 12)

    width = 500
    y = 800

    words = result.split()
    line = ""

    for word in words:

        test_line = line + word + " "

        if c.stringWidth(test_line, "Helvetica", 12) < width:
            line = test_line
        else:
            c.drawString(50, y, line)
            y -= 20
            line = word + " "

    if line:
        c.drawString(50, y, line)

    c.save()

    return FileResponse(file_path, media_type="application/pdf", filename="AI_Result.pdf")