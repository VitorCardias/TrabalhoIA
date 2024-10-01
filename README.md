# TrabalhoIA
Este projeto é uma aplicação web que utiliza a API Google AI (Gemini) para gerar respostas a partir de prompts textuais e arquivos multimídia (imagens e vídeos).
## Funcionalidades
- Upload de imagens e vídeos para serem processados pelo modelo Generative AI.
- Geração de conteúdo com base em prompts textuais e arquivos enviados.
- Exibição do tempo de processamento das respostas.
## Requisitos
Para executar este projeto, você precisará ter os seguintes pacotes e ferramentas instalados:
- Python
- Flask
- Pillow (para manipulação de imagens)
- google-generativeai (biblioteca para interagir com a API da Google)
- Werkzeug (para manipulação de arquivos)
## Instalação
1. Clone o repositório em sua máquina local:
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
```
2. Acesse o diretório do projeto:
```bash
cd seu-repositorio
```
3. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # No Windows use `venv\Scripts\activate`
```
4. Instale as dependências do projeto:
```bash
pip install -r requirements.txt
```
5. Crie um arquivo .env na raiz do projeto e adicione sua chave da API Google Generative AI:
```bash
touch .env
```
Dentro do arquivo .env, adicione a linha abaixo com sua chave da API:
```
API_KEY="sua-chave-da-api"
```
## Como Executar
1. Certifique-se de que o ambiente virtual está ativado (se você estiver usando um).
2. Execute o seguinte comando para iniciar a aplicação:
```bash
python app.py
```
3. Acesse a aplicação no seu navegador no endereço: `http://127.0.0.1:5000`