from flask import Flask, render_template, request, url_for, send_from_directory, session
import os
import markdown
from werkzeug.utils import secure_filename
import google.generativeai as genai
import PIL.Image
import time
import datetime
from dotenv import load_dotenv
from markupsafe import Markup

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração da API Gemini
genai.configure(api_key=os.getenv("API_KEY"))

# Configuração do Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mkv'}

chat_session = None

# Função para converter Markdown em HTML seguro
def markdown_to_html(text):
    return Markup(markdown.markdown(text))

# Registra o filtro no Jinja
app.jinja_env.filters['markdown_to_html'] = markdown_to_html

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
    
# Função para processar a conversa com os personagens
def process_conversation(prompt, file_path):
    global chat_session

    history = session.get('history', [])
    # Cria uma nova sessão se não existir
    if chat_session is None:
        chat_session = model.start_chat(
            # ... (histórico inicial)
            history=[
                        {
                            "role": "model",
                            "parts": "Você é um caminhoneiro debochado e irônico. Suas respostas devem incluir gírias de caminhoneiro e referências a lugares por onde você já passou. Atualmente, você está em um posto de gasolina no meio da estrada."
                        },
            ]
        )
    if file_path:
        # Adiciona o video ao histórico
        history.append({"role": "user", "parts": [file_path]})
    # Adiciona o prompt ao histórico
    history.append({"role": "user", "parts": [prompt]})

    # Envia a mensagem para a sessão existente
    response = chat_session.send_message(prompt)

    # Adiciona a resposta ao histórico
    history.append({"role": "assistant", "parts": [response]})

    return response

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
                response = process_conversation(inputs, False)
                for chunk in response:
                    response_text += chunk.text
            else:
                # Para vídeos
                response = process_conversation(prompt, processed_file)
                for chunk in response:
                    response_text += chunk.text
                response_text = markdown.markdown(response_text)
        else:
            # Se nenhum arquivo for enviado, apenas gera o conteúdo com o prompt de texto
            response = process_conversation(prompt, False)
            for chunk in response:
                response_text += chunk.text

        end_time = datetime.datetime.now()  # Tempo final de processamento
        processing_time = (end_time - start_time).total_seconds()  # Calcula o tempo em segundos

        response_history = session.get('history', [])
        return render_template('index.html', response=response_text, file_url=file_url, processing_time=processing_time, response_history=response_history)
    
    # Recupera o histórico ao renderizar a página
    response_history = session.get('history', [])
    return render_template('index.html', response_history=response_history)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
