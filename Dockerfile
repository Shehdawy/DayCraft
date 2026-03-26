FROM python:3.11-slim as builder

WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage - minimal
FROM python:3.11-slim

WORKDIR /app

# Copy installed deps from builder
COPY --from=builder /root/.local /root/.local

# Runtime deps only (no gcc)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --user streamlit

COPY . .

# Fix permissions
RUN chmod +x /root/.local/bin/*

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8503

HEALTHCHECK CMD curl --fail http://localhost:8503/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8503", "--server.address=0.0.0.0", "--server.headless=true"]

