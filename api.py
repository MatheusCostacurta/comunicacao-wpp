import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from typing import Dict, Any

from src.comunicacao_wpp_ia.aplicacao.servicos.conversasao import processar_mensagem
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.persistencia_conversa.redis_adapter import AdaptadorRedis
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.persistencia_conversa.memoria_local_adapter import AdaptadorMemoriaLocal
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.llm.groq_adapter import AdaptadorGroq
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.entrada.whatsapp.zapi_adapter import AdaptadorZAPI

# --- 1. Inicialização da Aplicação e Carregamento de Configurações ---
# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Cria a instância principal da aplicação FastAPI
app = FastAPI(
    title="API de Comunicação com WhatsApp",
    description="Esta API serve como um adaptador de entrada para receber e processar webhooks da Z-API.",
    version="1.0.0"
)

# --- 2. Injeção de Dependência (Singleton) ---
# Para garantir que os adaptadores sejam inicializados apenas uma vez e reutilizados
# em todas as requisições, seguimos o padrão Singleton.
def inicializar_adaptadores():
    """
    Inicializa e retorna instâncias únicas dos adaptadores necessários para a aplicação.
    A escolha do gerenciador de memória (Redis ou Local) é feita com base na variável de ambiente.
    """
    print("--- INICIALIZANDO ADAPTADORES DA APLICAÇÃO ---")
    llm = AdaptadorGroq()
    whatsapp = AdaptadorZAPI()

    ambiente = os.getenv("AMBIENTE", "dev")
    if ambiente == "prod":
        gerenciador_memoria = AdaptadorRedis()
    else:
        gerenciador_memoria = AdaptadorMemoriaLocal()
    
    return llm, gerenciador_memoria, whatsapp

# Instancia os adaptadores que serão usados nas rotas
llm_adapter, memoria_adapter, whatsapp_adapter = inicializar_adaptadores()


# --- 3. Definição das Rotas (Endpoints) ---
@app.post("/webhook/zapi", status_code=200)
async def receber_webhook_zapi(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint para receber as notificações (webhooks) da Z-API.

    Esta rota é o ponto de entrada principal para as mensagens do WhatsApp.
    1. Recebe o payload JSON da Z-API.
    2. Usa o AdaptadorZAPI para traduzir o payload em um DTO da aplicação.
    3. Adiciona o processamento da mensagem a uma tarefa em segundo plano (BackgroundTasks)
       para retornar uma resposta 200 OK imediatamente para a Z-API, evitando timeouts.
    """
    try:
        payload = await request.json()
        print(f"\n[API] Webhook Z-API recebido: {payload}")

        # O adaptador `receber` valida e converte o payload em um DTO padronizado
        mensagem_recebida = whatsapp_adapter.receber(payload)
        
        # Usamos tarefas em background para processar a lógica principal.
        # Isso libera a API para responder imediatamente, uma prática recomendada para webhooks.
        background_tasks.add_task(
            processar_mensagem,
            mensagem=mensagem_recebida.texto_conteudo,
            numero_telefone=mensagem_recebida.telefone_remetente,
            memoria=memoria_adapter,
            llm=llm_adapter
        )
        
        return {"status": "Mensagem recebida e agendada para processamento."}

    except ValueError as e:
        # Erro de validação do Pydantic no adaptador ou falha no download de mídia
        print(f"[API ERROR] Erro ao processar o payload do webhook: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Captura outros erros inesperados
        print(f"[API CRITICAL] Erro inesperado no endpoint do webhook: {e}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno no servidor.")