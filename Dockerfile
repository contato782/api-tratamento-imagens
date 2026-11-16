# Usa uma base Linux leve com Python
FROM python:3.9-slim

# Bloqueia qualquer tela interativa de instalação do Linux
ENV DEBIAN_FRONTEND=noninteractive

# Atualiza e instala o Tesseract OCR e dependências do OpenCV de forma silenciosa e limpa
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends tesseract-ocr libgl1-mesa-glx libglib2.0-0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Define a pasta de trabalho
WORKDIR /app
COPY . /app

# Instala as bibliotecas do Python
RUN pip install --no-cache-dir -r requirements.txt

# Inicia a API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
