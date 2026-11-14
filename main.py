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
        # 1. Isola apenas o texto do Base64 e remove espaços em branco residuais
        base64_str = req.imagem_base64.split(",")[-1].strip()
        
        # 2. Prevenção de falhas (Padding): Adiciona os sinais de '=' finais se o n8n os tiver cortado
        base64_str += "=" * ((4 - len(base64_str) % 4) % 4)
        
        # 3. Descodifica a imagem para matriz do OpenCV
        img_data = base64.b64decode(base64_str)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("A imagem chegou vazia ou num formato irreconhecível pelo OpenCV.")

        # ==========================================
        # 4. PIPELINE DE TRATAMENTO OTIMIZADO PARA IA
        # ==========================================
        
        # Passo A: Tons de Cinza (Remove as casas decimais vermelhas pelo contraste de cor)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Passo B: CLAHE - Equalização de Histograma Adaptativa
        # Nivela a iluminação da imagem: clareia as sombras e escurece os reflexos fortes, 
        # sem destruir a textura natural do vidro e dos números.
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(gray)
        
        # Nota: A binarização (adaptiveThreshold) e o desfoque intenso (medianBlur) 
        # foram removidos para evitar o "apagamento" de dígitos finos ou sujos.

        # ==========================================

        # 5. Recodifica a imagem final tratada para Base64
        _, buffer = cv2.imencode('.jpg', contrast)
        img_str = base64.b64encode(buffer).decode('utf-8')
        
        # Devolve ao n8n no formato exato que a OpenAI exige
        return {"imagem_processada": f"data:image/jpeg;base64,{img_str}"}

    except Exception as e:
        # Devolve o log de erro limpo para facilitar a depuração no n8n
        raise HTTPException(status_code=500, detail=f"Erro interno no Python: {str(e)}")


#from fastapi import FastAPI, HTTPException
#from pydantic import BaseModel
#import cv2
#import numpy as np
#import base64

#app = FastAPI()
#
#class ImagemRequest(BaseModel):
#    imagem_base64: str

#@app.post("/processar")
#def processar_imagem(req: ImagemRequest):
#    try:
        # 1. Isola apenas o texto do Base64
 #       base64_str = req.imagem_base64.split(",")[-1].strip()
        
        # 2. CORREÇÃO CRÍTICA: Adiciona o padding faltante (os sinais de '=')
#        base64_str += "=" * ((4 - len(base64_str) % 4) % 4)
        
        # 3. Decodifica a imagem
#        img_data = base64.b64decode(base64_str)
#        np_arr = np.frombuffer(img_data, np.uint8)
#        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#        if img is None:
#            raise ValueError("A imagem chegou vazia ou em um formato irreconhecível pelo OpenCV.")

        # 4. Pipeline OpenCV: Tons de cinza, CLAHE e Desfoque
#        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
#        contrast = clahe.apply(gray)
#        blurred = cv2.medianBlur(contrast, 5)

        # 5. Binarização Adaptativa
#        thresh = cv2.adaptiveThreshold(
#            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 61, 20    
#        )

        # 6. Recodifica e devolve
3        _, buffer = cv2.imencode('.jpg', thresh)
#        img_str = base64.b64encode(buffer).decode('utf-8')
        
#       return {"imagem_processada": f"data:image/jpeg;base64,{img_str}"}

#    except Exception as e:
        # Agora o erro 500 vai te dizer EXATAMENTE o que quebrou
#        raise HTTPException(status_code=500, detail=f"Erro interno no Python: {str(e)}")
