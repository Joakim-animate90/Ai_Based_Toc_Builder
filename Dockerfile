# syntax=docker/dockerfile:1

# Build Stage
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /build

# Install system dependencies required for PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && pip install -r requirements.txt

# Runtime Stage
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -g 1001 appuser && \
    useradd -u 1001 -g appuser -s /bin/bash -m appuser && \
    mkdir -p /home/appuser && \
    chown -R appuser:appuser /home/appuser

# Install runtime dependencies for PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser . .

# Ensure all files in /app are owned by appuser
RUN chown -R appuser:appuser /app

# Create directory for TOC outputs with proper permissions
RUN mkdir -p toc && chown -R appuser:appuser toc

# Ensure the SQLite DB file exists and is owned by appuser
RUN touch open_ai_db.sqlite && chown appuser:appuser open_ai_db.sqlite

# Switch to non-root user
USER appuser

# Set up healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/toc/health || exit 1

# Expose port
EXPOSE 8000

# Add metadata
LABEL maintainer="Joakim Bwire" \
      version="1.0.0" \
      description="AI-based table of contents extraction service"

# Set default environment variables
ENV OPENAI_MODEL="gpt-4.1-mini" \
    PDF_MAX_PAGES=5 \
    DEFAULT_THREAD_COUNT=4 \
    PORT=8000 \
    LOG_LEVEL=warning \
    OPENAI_DB_PATH="open_ai_db.sqlite" \
    RECORD_AGE_MINUTES=180
    

# Command to run the application in production mode
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers", "--no-access-log", "--log-level", "warning"]
