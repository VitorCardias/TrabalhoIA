import os
import time
import google.generativeai as genai

genai.configure(api_key=os.getenv("API_KEY"))

def upload_to_gemini(path, mime_type=None):
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

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

# Create the model
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

files = [
  upload_to_gemini("American Museum of Natural History Tour - 5 Min", mime_type="video/mp4"),
]

wait_for_files_active(files)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        files[0],
      ],
    },
    {
      "role": "user",
      "parts": [
        "o que esta acontecendo no video?",
      ],
    },
    {
      "role": "model",
      "parts": [
        "O vídeo mostra um tour pela ala de dinossauros do Museu Americano de História Natural. O vídeo inclui esqueletos de dinossauros, incluindo um esqueleto de Apatossauro, bem como uma variedade de exposições explicando a evolução dos dinossauros. \n",
      ],
    },
  ]
)

response = chat_session.send_message("INSERT_INPUT_HERE")

print(response.text)