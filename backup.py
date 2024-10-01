import google.generativeai as genai
import PIL.Image
import os
import cv2
import numpy as np
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

img = './logo-hamburguer.png'

# Verifica se o arquivo de imagem existe
if os.path.exists(img):
    img = PIL.Image.open(img).resize((256, 256))
else:
    img = None

prompt = input('PROMPT:')

inputs = [prompt]
if img:
    inputs.append(img)

response = model.generate_content(inputs, stream=True)

for chunk in response:
    print(chunk.text)
    print("_" * 80)