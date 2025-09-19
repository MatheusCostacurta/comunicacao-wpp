import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

from api import app # Importa a instância do FastAPI do arquivo api.py

def run():
    """
    Ponto de entrada principal da aplicação.
    Inicia o servidor uvicorn para servir a API FastAPI.
    """
    print("--- INICIANDO SERVIDOR DA API DE COMUNICAÇÃO WPP ---")
    
    # Obtém a porta da variável de ambiente PORT. O padrão é 8000 para desenvolvimento local.
    port = int(os.environ.get("PORT", 8000))

    # O uvicorn.run inicia o servidor.
    # "api:app" informa ao uvicorn para procurar o objeto 'app' no arquivo 'api.py'.
    # host="0.0.0.0" torna a API acessível na rede local.
    # port=8000 define a porta..
    uvicorn.run("api:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    run()