from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
import google.generativeai as genai
import PIL.Image
import time
import datetime
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração da API Gemini
genai.configure(api_key=os.getenv("API_KEY"))

# Configuração do Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mkv'}

# Função para checar extensão de arquivo permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Função para fazer upload de arquivo para o modelo (tanto imagem quanto vídeo)
def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    return file

# Função para esperar o processamento dos arquivos
def wait_for_files_active(files):
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
        
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

# Função para processar o arquivo (imagem ou vídeo)
def process_file(file_path):
    file_extension = file_path.split('.')[-1].lower()

    # Verifica se é uma imagem ou vídeo
    if file_extension in ['png', 'jpg', 'jpeg', 'bmp', 'gif']:
        # Tratamento de imagem
        img = PIL.Image.open(file_path).resize((256, 256))
        return img
    elif file_extension in ['mp4', 'avi', 'mov', 'mkv']:
        # Tratamento de vídeo
        file = upload_to_gemini(file_path, mime_type="video/mp4")
        wait_for_files_active([file])
        return file
    else:
        raise Exception("Tipo de arquivo não suportado. Use imagens ou vídeos.")

# Rota para exibir arquivos de uploads
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Rota principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_time = datetime.datetime.now()  # Inicia o tempo de processamento
        prompt = request.form['prompt']  # Prompt inserido pelo usuário
        file = request.files.get('file')  # Arquivo de imagem ou vídeo (opcional)
        response_text = ""  # Inicializa a variável para a resposta
        file_url = None  # Inicializa a URL do arquivo para exibição

        # Se o arquivo for fornecido e permitido
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Processa o arquivo (imagem ou vídeo)
            processed_file = process_file(file_path)
            file_url = url_for('uploaded_file', filename=filename)

            # Geração de conteúdo com base no arquivo e no prompt
            if isinstance(processed_file, PIL.Image.Image):
                # Para imagens
                inputs = [prompt, processed_file]
                response = model.generate_content(inputs, stream=True)
                for chunk in response:
                    response_text += chunk.text
            else:
                # Para vídeos
                chat_session = model.start_chat(
                    history=[
                        {
                            "role": "user",
                            "parts": [processed_file],
                        },
                        {
                            "role": "user",
                            "parts": [prompt],
                        },
                    ]
                )
                response = chat_session.send_message(prompt)
                response_text = response.text
        else:
            # Se nenhum arquivo for enviado, apenas gera o conteúdo com o prompt de texto
            response = model.generate_content([prompt], stream=True)
            for chunk in response:
                response_text += chunk.text

        end_time = datetime.datetime.now()  # Tempo final de processamento
        processing_time = (end_time - start_time).total_seconds()  # Calcula o tempo em segundos

        return render_template('index.html', response=response_text, file_url=file_url, processing_time=processing_time)

    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
