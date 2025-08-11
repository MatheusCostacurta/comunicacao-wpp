# 1. Imagem Base: Começamos com uma imagem oficial e leve do Python.
FROM python:3.10-slim

# 2. Diretório de Trabalho: Define o diretório padrão dentro do contêiner.
WORKDIR /app

# 3. Copia e Instala as Dependências:
# Copia apenas o requirements.txt primeiro para aproveitar o cache do Docker.
# O Docker só reinstalará as dependências se este arquivo mudar.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia o Código da Aplicação: Copia todos os outros arquivos do seu projeto.
COPY . .

# 5. Comando de Execução: Define o comando que será executado quando o contêiner iniciar.
CMD ["python", "main.py"]