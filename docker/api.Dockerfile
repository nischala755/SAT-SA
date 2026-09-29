FROM python:3.12.10-slim AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/apps/api:/app/analytics:/app/packages/analytics-contracts \
    SAT_SA_STORAGE_ROOT=/var/lib/sat-sa SAT_SA_DEMO_MODE=true
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock
COPY apps/api apps/api
COPY analytics analytics
COPY packages/analytics-contracts packages/analytics-contracts
COPY config config
COPY scripts/generate_demo.py scripts/generate_demo.py
RUN groupadd --gid 10001 satsa && useradd --uid 10001 --gid satsa --no-create-home satsa \
    && mkdir -p /var/lib/sat-sa && chown satsa:satsa /var/lib/sat-sa
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=5s --start-period=60s --retries=6 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=3)"
CMD ["sh", "-c", "python -m sat_sa.synthetic.bootstrap && exec python -m uvicorn sat_sa_api.main:create_app --factory --host 0.0.0.0 --port 8000 --workers 1"]
