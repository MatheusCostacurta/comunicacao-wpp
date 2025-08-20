import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from typing import Dict, Any

from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.persistencia_conversa.redis_adapter import AdaptadorRedis
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.persistencia_conversa.memoria_local_adapter import AdaptadorMemoriaLocal
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.llm.groq_adapter import AdaptadorGroq
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.entrada.whatsapp.zapi_adapter import AdaptadorZAPI
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.repositorios.agriwin_ferramentas import RepoAgriwinFerramentas
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.repositorios.agriwin_remetente import RepoAgriwinRemetente
from src.comunicacao_wpp_ia.aplicacao.dtos.mensagem_recebida import MensagemRecebida
from src.comunicacao_wpp_ia.aplicacao.servicos.conversasao import ServicoConversa

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
def inicializar_servicos_e_adaptadores():
    """
    Inicializa e retorna instâncias únicas dos adaptadores necessários para a aplicação.
    A escolha do gerenciador de memória (Redis ou Local) é feita com base na variável de ambiente.
    """
    print("--- INICIALIZANDO ADAPTADORES DA APLICAÇÃO ---")
    llm_adapter = AdaptadorGroq()
    whatsapp_adapter = AdaptadorZAPI()
    repo_remetente = RepoAgriwinRemetente()

    ambiente = os.getenv("AMBIENTE", "dev")
    if ambiente == "prod":
        memoria_adapter = AdaptadorRedis()
    else:
        memoria_adapter = AdaptadorMemoriaLocal()

    servico_conversa = ServicoConversa(
        memoria = memoria_adapter,
        llm = llm_adapter,
        repo_remetente = repo_remetente
    )
    
    return servico_conversa, whatsapp_adapter

# Instancia os adaptadores que serão usados nas rotas
servico_conversa, whatsapp_adapter = inicializar_servicos_e_adaptadores()


def processar_webhook_em_background(mensagem: MensagemRecebida):
    """
    Função de trabalho executada em segundo plano.
    1. Obtém os dados do remetente.
    2. Se o remetente for encontrado, inicia o processamento da mensagem.
    """
    # Etapa 1: Obter o remetente
    remetente = servico_conversa.obter_remetente(telefone=mensagem.telefone_remetente)

    # Etapa 2: Chamar o processamento principal apenas se o remetente existir
    if remetente:
        servico_conversa.processar_mensagem(mensagem=mensagem.texto_conteudo, remetente=remetente)
    # Se o remetente não for encontrado, a tarefa termina silenciosamente.
    # O erro já foi logado pela função obter_remetente.

# --- 3. Definição das Rotas (Endpoints) ---
@app.post("/webhook/zapi", status_code=200)
async def receber_webhook_zapi(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint para receber as notificações (webhooks) da Z-API.
    """
    try:
        payload = await request.json()
        print(f"\n[API] Webhook Z-API recebido: {payload}")

        # O adaptador `receber` valida e converte o payload em um DTO padronizado
        mensagem_recebida = whatsapp_adapter.receber(payload)
        
        # Usamos tarefas em background para processar a lógica principal.
        # Isso libera a API para responder imediatamente, uma prática recomendada para webhooks.
        background_tasks.add_task(
            processar_webhook_em_background,
            mensagem=mensagem_recebida
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