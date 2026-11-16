FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Atualiza a lista de pacotes isoladamente
RUN apt-get update

# Instala o Tesseract OCR
RUN apt-get install -y tesseract-ocr

# Instala as dependências de vídeo corretas para o OpenCV no Debian moderno
RUN apt-get install -y libgl1 libglib2.0-0

# Limpa o cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
