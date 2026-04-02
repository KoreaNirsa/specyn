FROM node:20-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CODEX_HOME=/workspace/.specyn/codex \
    VIRTUAL_ENV=/opt/specyn-venv \
    PATH=/opt/specyn-venv/bin:${PATH}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        git \
        python3 \
        python3-pip \
        python3-venv \
    && ln -sf /usr/bin/python3 /usr/local/bin/python \
    && python -m venv "${VIRTUAL_ENV}" \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY dashboard/ai-server/requirements.txt /tmp/dashboard-requirements.txt
COPY dashboard/ai-server/requirements-dev.txt /tmp/dashboard-requirements-dev.txt
COPY tools/requirements.txt /tmp/tools-requirements.txt

RUN python -m pip install --upgrade pip \
    && python -m pip install \
        -r /tmp/dashboard-requirements.txt \
        -r /tmp/dashboard-requirements-dev.txt \
        -r /tmp/tools-requirements.txt \
    && npm i -g @openai/codex@latest \
    && codex --version
