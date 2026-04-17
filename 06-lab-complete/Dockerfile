# ============================================================
# Production Dockerfile — Multi-stage, < 500 MB, non-root
# ============================================================

# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-slim AS runtime

# Tạo non-root user, đặt home là /app
RUN groupadd -r agent && useradd -r -g agent -d /app agent

WORKDIR /app

# Copy packages từ builder vào thư mục home của user agent (/app/.local)
COPY --from=builder /root/.local /app/.local

# Copy application
COPY app/ ./app/
COPY utils/ ./utils/

# Đảm bảo quyền sở hữu
RUN chown -R agent:agent /app

USER agent

# Cấu hình Path để nhận diện các thư viện đã cài
ENV PATH=/app/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Railway sẽ tự động quản lý cổng thông qua biến môi trường PORT

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start command: Hỗ trợ biến $PORT của Railway, mặc định 8000 nếu chạy local
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
