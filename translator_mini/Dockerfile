# Multi-arch Dockerfile for Chatbot Translator Mini
# Compatible with both x86_64 (Docker Desktop Windows/Mac) and ARM (Orange Pi)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# - portaudio19-dev: for microphone access via PyAudio
# - espeak: for offline TTS
# - alsa-utils: audio utilities
# - gcc, g++: for compiling PyAudio
RUN apt-get update && apt-get install -y --no-install-recommends \
    portaudio19-dev \
    espeak \
    alsa-utils \
    gcc \
    g++ \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .

# Create non-root user for security
RUN useradd -m -u 1000 chatbot && \
    chown -R chatbot:chatbot /app

USER chatbot

# Default command: show help
CMD ["python3", "main.py", "--help"]
