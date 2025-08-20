import uvicorn
from api import app  # Importa a instância do FastAPI do arquivo api.py

def run():
    """
    Ponto de entrada principal da aplicação.
    Inicia o servidor uvicorn para servir a API FastAPI.
    """
    print("--- INICIANDO SERVIDOR DA API DE COMUNICAÇÃO WPP ---")
    
    # O uvicorn.run inicia o servidor.
    # "api:app" informa ao uvicorn para procurar o objeto 'app' no arquivo 'api.py'.
    # host="0.0.0.0" torna a API acessível na rede local.
    # port=8000 define a porta.
    # reload=True reinicia o servidor automaticamente quando detecta alterações no código.
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()