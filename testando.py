import google.generativeai as genai
import PIL.Image
import os
import cv2
import numpy as np
import time
from dotenv import load_dotenv

load_dotenv()

# Configuração da API Gemini
genai.configure(api_key=os.getenv("API_KEY"))

# Função para fazer upload de arquivo para o modelo (tanto imagem quanto vídeo)
def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

# Função para esperar o processamento dos arquivos
def wait_for_files_active(files):
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

# Configuração do modelo generativo
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Função principal que verifica se o arquivo é imagem ou vídeo
def process_file(file_path):
    file_extension = file_path.split('.')[-1].lower()

    # Verifica se é uma imagem ou vídeo
    if file_extension in ['png', 'jpg', 'jpeg', 'bmp', 'gif']:
        # Tratamento de imagem
        if os.path.exists(file_path):
            img = PIL.Image.open(file_path).resize((256, 256))
            print(f"Processando imagem {file_path}")
            return img
        else:
            raise Exception(f"Imagem {file_path} não encontrada.")
    elif file_extension in ['mp4', 'avi', 'mov', 'mkv']:
        # Tratamento de vídeo
        print(f"Processando vídeo {file_path}")
        file = upload_to_gemini(file_path, mime_type="video/mp4")
        wait_for_files_active([file])
        return file
    else:
        raise Exception("Tipo de arquivo não suportado. Use imagens ou vídeos.")

# Prompt do usuário
prompt = input('PROMPT:')

# Caminho do arquivo (pode ser imagem ou vídeo)
file_path = input("Insira o caminho do arquivo (imagem ou vídeo): ")

# Processa o arquivo (imagem ou vídeo)
processed_file = process_file(file_path)

# Geração de conteúdo com base no arquivo e no prompt
if isinstance(processed_file, PIL.Image.Image):
    # Para imagens
    inputs = [prompt, processed_file]
    response = model.generate_content(inputs, stream=True)
    for chunk in response:
        print(chunk.text)
        print("_" * 80)
else:
    # Para vídeos
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    processed_file,
                ],
            },
            {
                "role": "user",
                "parts": [
                    prompt,
                ],
            },
        ]
    )
    response = chat_session.send_message(prompt)
    print(response.text)