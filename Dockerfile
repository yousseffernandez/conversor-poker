FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto
COPY . .

# Instala as dependências necessárias
RUN pip install streamlit

EXPOSE 8080

# Configura o Streamlit para rodar na porta padrão do Google Cloud
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
