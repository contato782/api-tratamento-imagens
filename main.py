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

        # ==========================================
        # PRÉ-PROCESSAMENTO AVANÇADO PARA TESSERACT
        # ==========================================
        
        # 1. Ampliação (CRUCIAL): Multiplica o tamanho da imagem por 3.
        # Imagens cortadas no n8n são muito pequenas para o motor OCR padrão.
        img_ampliada = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

        # 2. Tons de Cinza
        gray = cv2.cvtColor(img_ampliada, cv2.COLOR_BGR2GRAY)
        
        # 3. Contraste Seguro (CLAHE) - clareia sombras sem estourar o brilho
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast = clahe.apply(gray)
        
        # 4. Desfoque sutil (Remove o "serrilhado" dos números gerado pela ampliação)
        blur = cv2.medianBlur(contrast, 3)

        # 5. Binarização extrema (Otsu - Preto e Branco absoluto)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # ==========================================
        # EXTRAÇÃO (DUPLA TENTATIVA)
        # ==========================================
        
        # Configuração: PSM 6 lê blocos de texto (tolera roldanas desalinhadas)
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
        
        # Tentativa A: Lê da imagem binarizada
        texto_extraido = pytesseract.image_to_string(thresh, config=custom_config)
        numeros_finais = re.sub(r'\D', '', texto_extraido)

        # Tentativa B (Failsafe): Se a binarização destruiu os traços e apagou o número,
        # tentamos ler diretamente da imagem cinza com alto contraste.
        if not numeros_finais:
            texto_extraido = pytesseract.image_to_string(contrast, config=custom_config)
            numeros_finais = re.sub(r'\D', '', texto_extraido)

        # Retorna o resultado final
        return {"leitura_final": numeros_finais if numeros_finais else ""}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
