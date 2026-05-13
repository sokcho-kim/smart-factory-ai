FROM python:3.11-slim

WORKDIR /app
COPY src/ai/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ai/ ./ai/

CMD ["uvicorn", "ai.server:app", "--host", "0.0.0.0", "--port", "8000"]
