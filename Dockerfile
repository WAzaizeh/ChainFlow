FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn uvicorn

# Use volume mount for local development
# COPY app/ .

# Use 8080 as internal port
ENV PORT=8080
ENV HOST=0.0.0.0
EXPOSE ${PORT}

CMD exec gunicorn main:app \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind ${HOST}:${PORT}