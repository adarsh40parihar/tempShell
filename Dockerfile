# Stage 1 — Build React frontend
FROM node:18-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install --production
COPY frontend/public ./public
COPY frontend/src ./src
RUN npm run build

# Stage 2 — Python backend (serves API + built frontend as static files)
FROM python:3.11-slim
WORKDIR /app

# System build dependencies
RUN apt-get update && apt-get install -y gcc g++ libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (cached unless requirements.txt changes)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend source structure
COPY backend/main.py .
COPY backend/utils/ ./utils/
COPY backend/models/ ./models/
COPY backend/controllers/ ./controllers/
COPY backend/routers/ ./routers/

# Copy built React app — FastAPI serves it as static files from /app/frontend/build
COPY --from=frontend-build /frontend/build ./frontend/build/

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
