FROM python:3.10-slim

# Install system dependencies for OCR (OpenCV) and Audio processing (Whisper needs ffmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Upgrade pip and install core build tools first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install the requirements
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
