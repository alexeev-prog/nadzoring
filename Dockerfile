# ====================== Builder stage ======================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# build deps for packages like netifaces
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install into a separate prefix so we can copy it to final
RUN pip install --no-cache-dir --prefix=/install .

# ====================== Final stage ======================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    iproute2 \
    traceroute \
    iputils-ping \
    dnsutils \
    whois \
    net-tools \
    procps \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy installed python packages + console scripts
COPY --from=builder /install /usr/local

# optional: non-root runtime
RUN useradd -m -u 10001 -s /usr/sbin/nologin appuser
USER appuser

ENTRYPOINT ["nadzoring"]
CMD ["--help"]