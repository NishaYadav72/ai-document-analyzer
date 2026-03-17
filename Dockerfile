FROM python:3.11

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y tesseract-ocr poppler-utils

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]