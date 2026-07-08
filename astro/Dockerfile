FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
  && rm -rf /var/lib/apt/lists/*

COPY astro/pyproject.toml .
COPY astro/src ./src

# Сборка через setuptools (см. pyproject.toml). Всегда bootstrap setuptools + --no-build-isolation (см. backend/Dockerfile).
# PIP_TRUSTED_HOSTS=1: curl -k и --trusted-host при перехвате TLS.
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

CMD ["uvicorn", "todayflow_astro.main:app", "--host", "0.0.0.0", "--port", "8081"]
