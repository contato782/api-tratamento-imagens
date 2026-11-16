from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cv2
import numpy as np
import base64
import pytesseract
import re

app = FastAPI()

class ImagemRequest(BaseModel):
    imagem_base64: str

@app.post("/processar")
def processar_imagem(req: ImagemRequest):
    try:
        # Decodifica o Base64
        base64_str = req.imagem_base64.split(",")[-1].strip()
        base64_str += "=" * ((4 - len(base64_str) % 4) % 4)
        
        img_data = base64.b64decode(base64_str)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Imagem chegou corrompida.")

        # Tratamento de Imagem Otimizado para Tesseract
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # O Tesseract exige contraste extremo (Preto no Branco). Usamos a Binarização de Otsu.
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Configuração do Tesseract: PSM 7 (linha única de texto) e whitelist (apenas números)
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
        texto_extraido = pytesseract.image_to_string(thresh, config=custom_config)
        
        # Filtra a resposta para garantir que apenas os números passem
        numeros_finais = re.sub(r'\D', '', texto_extraido)

        # Se não ler nada, devolve vazio para o n8n bloquear a inserção
        return {"leitura_final": numeros_finais if numeros_finais else ""}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
