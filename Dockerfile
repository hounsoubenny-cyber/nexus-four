# ============================================
# NEXUS-FOUR v2.1 - Image Docker Optimisée
# Compatible: Ubuntu, Fedora, Debian, Arch...
# SELinux-ready | Multi-distro
# ============================================

FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

COPY conversation_app/requirements.txt .
RUN pip install --upgrade pip \
    -r requirements.txt \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --timeout 180 \
    --retries 10 \
    && rm -rf /root/.cache/pip/*

COPY conversation_app/requirements2.txt .
RUN pip install -r requirements2.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --timeout 180 \
    --retries 10 \
    && rm -rf /root/.cache/pip/*

# ============================================
# Image finale
# ============================================
FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

WORKDIR /app

# Copie des dépendances depuis le builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copie du code
COPY conversation_app/ conversation_app/
COPY frontend/REACT/build/ frontend/REACT/build/

# Création des dossiers runtime
RUN mkdir -p \
    /app/conversation_app/var/cache \
    /app/conversation_app/fastapi_mount/hub/imgs_profile \
    /app/conversation_app/fastapi_mount/nexus_files \
    /app/conversation_app/chat_nexus/MODEL \
    /app/conversation_app/chat_nexus/DOCS_IFRI \
    /app/conversation_app/chat_nexus/index

# Nettoyage __pycache__
RUN find /app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /app -type f -name "*.pyc" -delete 2>/dev/null || true

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

LABEL maintainer="Nexus-Four Team" \
      version="2.1" \
      description="Nexus-Four : FastAPI + React SPA + LLM local + RAG"

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

WORKDIR /app/conversation_app

CMD ["python", "run_api.py"]
