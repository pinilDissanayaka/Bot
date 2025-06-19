FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        g++ \
        cmake \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir psycopg2-binary && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8070

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8070"]
