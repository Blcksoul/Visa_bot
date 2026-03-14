FROM python:3.11-slim

# ── System dependencies ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Python dependencies ───────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Install Playwright browsers ───────────────────────────────────────────────
RUN playwright install chromium --with-deps

# ── Copy application code ─────────────────────────────────────────────────────
COPY . .

# ── Run the bot ───────────────────────────────────────────────────────────────
CMD ["python", "bot.py"]
