FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libgobject-2.0-0 \
    libglib2.0-0 \
    shared-mime-info \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    zlib1g \
    fonts-dejavu-core \
    curl \
  && rm -rf /var/lib/apt/lists/*

COPY backend /app
COPY CONTENT /CONTENT
COPY DATA /DATA

ENV CONTENT_DIR="/CONTENT"
ENV TODAYFLOW_DATA_DIR="/DATA"

# Не делаем `pip install -U pip` — см. astro/Dockerfile.
# Всегда кладём setuptools с files.pythonhosted.org и ставим пакет с --no-build-isolation,
# чтобы не дергать отдельный pip в изолированной сборке (частые сбои DNS/прокси на PyPI).
# PIP_TRUSTED_HOSTS=1: curl -k и --trusted-host для TLS в корпоративных сетях.
ARG PIP_TRUSTED_HOSTS=0
RUN set -eux; \
    opts="--no-cache-dir"; \
    if [ "$PIP_TRUSTED_HOSTS" = "1" ]; then \
      opts="$opts --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org"; \
      curl -kfsSL -o /tmp/setuptools-82.0.1-py3-none-any.whl \
        "https://files.pythonhosted.org/packages/9d/76/f789f7a86709c6b087c5a2f52f911838cad707cc613162401badc665acfe/setuptools-82.0.1-py3-none-any.whl"; \
    else \
      curl -fsSL -o /tmp/setuptools-82.0.1-py3-none-any.whl \
        "https://files.pythonhosted.org/packages/9d/76/f789f7a86709c6b087c5a2f52f911838cad707cc613162401badc665acfe/setuptools-82.0.1-py3-none-any.whl"; \
    fi; \
    pip install --no-cache-dir --no-deps /tmp/setuptools-82.0.1-py3-none-any.whl; \
    rm -f /tmp/setuptools-82.0.1-py3-none-any.whl; \
    pip install $opts --no-build-isolation .

CMD ["uvicorn", "todayflow_backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
