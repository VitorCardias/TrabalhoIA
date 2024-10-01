import google.generativeai as genai
import PIL.Image
import os
import cv2
import numpy as np
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def process_media(file_path, prompt):
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    # Verificar o tipo de mídia
    if file_path.endswith(".png") or file_path.endswith(".jpg"):
        # Processar imagem (lógica do Código A)
        img = PIL.Image.open(file_path).resize((256, 256))
        inputs = [prompt]
        if img:
            inputs.append(img)
        response = model.generate_content(inputs, stream=True)
        for chunk in response:
            return chunk.text

    elif file_path.endswith(".mp4") or file_path.endswith(".avi"):
        # Processar vídeo (lógica do Código B)
        # ... (lógica de upload, espera e criação da sessão de chat)
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(prompt)
        return response.text

    else:
        raise ValueError("Formato de arquivo não suportado")

# Exemplo de uso
file_path = input("Digite o caminho para o arquivo (imagem ou vídeo): ")
prompt = input("Digite o prompt: ")

try:
    result = process_media(file_path, prompt)
    print(result)
except Exception as e:
    print(f"Erro: {str(e)}")