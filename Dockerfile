# Usa uma base Linux leve com Python
FROM python:3.9-slim

# Instala as ferramentas do sistema necessárias e o motor Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr libgl1-mesa-glx libglib2.0-0

# Define a pasta de trabalho
WORKDIR /app
COPY . /app

# Instala as bibliotecas do Python
RUN pip install --no-cache-dir -r requirements.txt

# Inicia a API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
