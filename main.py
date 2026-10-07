from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cv2
import numpy as np
import base64

app = FastAPI()

class ImagemRequest(BaseModel):
    imagem_base64: str

@app.post("/processar")
def processar_imagem(req: ImagemRequest):
    try:
        # Decodifica o Base64 recebido do n8n
        img_data = base64.b64decode(req.imagem_base64.split(",")[-1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Imagem inválida.")

        # Pipeline OpenCV: Tons de cinza, CLAHE (contraste) e Desfoque
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(gray)
        blurred = cv2.medianBlur(contrast, 5)

        # Binarização Adaptativa (Preto e Branco extremo)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 5
        )

        # Recodifica para Base64 para devolver ao n8n
        _, buffer = cv2.imencode('.jpg', thresh)
        img_str = base64.b64encode(buffer).decode('utf-8')

        return {"imagem_processada": f"data:image/jpeg;base64,{img_str}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
