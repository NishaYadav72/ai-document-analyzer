# 1) base image
FROM python:3.11-slim

# 2) install poppler + tesseract
RUN apt-get update && \
    apt-get install -y poppler-utils tesseract-ocr && \
    apt-get clean

# 3) set workdir
WORKDIR /app

# 4) copy requirements
COPY requirements.txt .

# 5) install python packages
RUN pip install --no-cache-dir -r requirements.txt

# 6) copy app code
COPY . .

# 7) expose port
EXPOSE 10000

# 8) run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]