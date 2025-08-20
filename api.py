import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks

from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.persistencia_conversa.redis_adapter import AdaptadorRedis
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.persistencia_conversa.memoria_local_adapter import AdaptadorMemoriaLocal
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.llm.groq_adapter import AdaptadorGroq
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.entrada.whatsapp.zapi_adapter import AdaptadorZAPI
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.repositorios.agriwin_remetente import RepoAgriwinRemetente

from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.pre_processamento_texto.whisper_adapter import AdaptadorWhisper
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.pre_processamento_texto.gemini_vision_adapter import AdaptadorGeminiVision

from src.comunicacao_wpp_ia.aplicacao.servicos.pre_processamento import PreProcessamentoService
from src.comunicacao_wpp_ia.aplicacao.servicos.conversasao import ServicoConversa
from src.comunicacao_wpp_ia.aplicacao.dtos.mensagem_recebida import MensagemRecebida


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
    print("--- INICIALIZANDO ADAPTADORES E SERVIÇOS DA APLICAÇÃO ---")
    
    # Adaptadores de Saída (Infraestrutura)
    llm_adapter = AdaptadorGroq()
    whatsapp_adapter = AdaptadorZAPI()
    repo_remetente = RepoAgriwinRemetente()
    whisper_adapter = AdaptadorWhisper()
    gemini_adapter = AdaptadorGeminiVision()

    ambiente = os.getenv("AMBIENTE", "dev")
    memoria_adapter = AdaptadorRedis() if ambiente == "prod" else AdaptadorMemoriaLocal()

    # Serviços de Aplicação (Core)
    pre_processador = PreProcessamentoService(
        servico_transcricao=whisper_adapter,
        servico_imagem=gemini_adapter
    )
    
    servico_conversa = ServicoConversa(
        memoria=memoria_adapter,
        llm=llm_adapter,
        repo_remetente=repo_remetente,
        pre_processador=pre_processador
    )
    
    return servico_conversa, whatsapp_adapter

servico_conversa, whatsapp_adapter = inicializar_servicos_e_adaptadores()

@app.post("/webhook/zapi", status_code=200)
async def receber_webhook_zapi(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
        print(f"\n[API] Webhook Z-API recebido: {payload}")

        mensagem_recebida = whatsapp_adapter.receber(payload)
        
        # A lógica de negócio é delegada para o serviço de aplicação em background
        background_tasks.add_task(
            servico_conversa.processar_mensagem_recebida,
            mensagem_recebida=mensagem_recebida
        )
        
        return {"status": "Mensagem recebida e agendada para processamento."}

    except ValueError as e:
        print(f"[API ERROR] Erro ao processar o payload do webhook: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[API CRITICAL] Erro inesperado no endpoint do webhook: {e}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno no servidor.")