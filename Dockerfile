FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY caminhos_minimos/ caminhos_minimos/
COPY complementos/ complementos/
COPY exemplos/ exemplos/

ENTRYPOINT ["python", "main.py"]
