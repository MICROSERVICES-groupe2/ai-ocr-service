FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng \
    poppler-utils libgl1 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install PyTorch CPU-only first (much smaller than CUDA version)
RUN pip install --no-cache-dir --timeout=300 \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout=300 -r requirements.txt

COPY app/ ./app/
COPY models/ ./models/
COPY tests/ ./tests/

EXPOSE 8086
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8086"]
