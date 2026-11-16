# Atualizamos para uma versão mais recente com repositórios ativos do Debian
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Adicionamos a permissão para atualizar repositórios antigos e removemos o modo silencioso
RUN apt-get update --allow-releaseinfo-change && \
    apt-get install -y --no-install-recommends tesseract-ocr libgl1-mesa-glx libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
