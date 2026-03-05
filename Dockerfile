FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY src /app/src
COPY pyproject.toml /app/

RUN mkdir -p /data && chown -R app:app /data /app

USER app

VOLUME ["/data"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -m macrocenter_stock_checker.cli healthcheck || exit 1

ENTRYPOINT ["python", "-m", "macrocenter_stock_checker.cli"]
CMD ["check-now"]
