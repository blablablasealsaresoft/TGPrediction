FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN useradd --system --create-home --shell /usr/sbin/nologin trader

WORKDIR /app

COPY requirements/dev.lock requirements/dev.lock
RUN pip install --upgrade pip && pip install -r requirements/dev.lock
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . .
RUN mkdir -p /app/logs && chown -R trader:trader /app

USER trader

ENTRYPOINT ["python", "scripts/run_bot.py"]
CMD ["--network", "devnet", "--no-auto-trade", "--read-only"]
