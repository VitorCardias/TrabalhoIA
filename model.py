import google.generativeai as genai
import PIL.Image
import os
import cv2
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def process_input(prompt, img_file):
    inputs = [prompt]
    
    if img_file:
        img = PIL.Image.open(img_file).resize((256, 256))
        inputs.append(img)
    
    response = model.generate_content(inputs, stream=True)
    
    output = ""
    for chunk in response:
        output += chunk.text + "\n"
    
    return output
