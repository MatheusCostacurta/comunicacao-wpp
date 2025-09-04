import os
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, UploadFile, File, Form

from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.persistencia_conversa.redis_adapter import AdaptadorRedis
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.persistencia_conversa.memoria_local_adapter import AdaptadorMemoriaLocal
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.llm.groq_adapter import AdaptadorGroq
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.entrada.whatsapp.zapi_adapter import AdaptadorZAPI
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.repositorios.agriwin_remetente import RepoAgriwinRemetente
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.repositorios.agriwin_consumo import RepoAgriwinConsumo

from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.pre_processamento_texto.whisper_adapter import AdaptadorWhisper
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.pre_processamento_texto.gemini_vision_adapter import AdaptadorGeminiVision

from src.comunicacao_wpp_ia.aplicacao.servicos.pre_processamento import PreProcessamentoService
from src.comunicacao_wpp_ia.aplicacao.servicos.conversasao import ServicoConversa
from src.comunicacao_wpp_ia.aplicacao.dtos.mensagem_recebida import MensagemRecebida

from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.clientes_api.agriwin_cliente import AgriwinCliente


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
    
    # Instancia o AgriwinCliente com as URLs do .env
    agriwin_urls = ["https://demo.agriwin.com.br"]
    agriwin_cliente = AgriwinCliente(base_urls=agriwin_urls)

    # Adaptadores de Saída (Infraestrutura)
    llm_adapter = AdaptadorGroq()
    whatsapp_adapter = AdaptadorZAPI()
    repo_remetente = RepoAgriwinRemetente(agriwin_cliente=agriwin_cliente)
    repo_consumo = RepoAgriwinConsumo(agriwin_cliente=agriwin_cliente)
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
        repo_consumo=repo_consumo,
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
    
@app.post("/webhook/zapi/test-audio", status_code=200, tags=["Testes"])
async def receber_audio_para_teste(
    background_tasks: BackgroundTasks,
    phone: str = Form(...),
    audio_file: UploadFile = File(...)
):
    """
    Endpoint de teste para simular o recebimento de uma mensagem de áudio via upload direto.
    """
    try:
        print(f"\n[API TEST] Áudio recebido para o telefone {phone} | Nome do arquivo: {audio_file.filename}")

        # Lê os bytes do arquivo de áudio enviado
        audio_bytes = await audio_file.read()

        # Cria o DTO padronizado da aplicação, assim como o adaptador da Z-API faria
        mensagem_recebida = MensagemRecebida(
            telefone_remetente=phone,
            tipo="AUDIO",
            media_conteudo=audio_bytes,
            media_mime_type=audio_file.content_type
        )
        
        # Delega para o mesmo serviço de aplicação, garantindo que o fluxo seja idêntico
        background_tasks.add_task(
            servico_conversa.processar_mensagem_recebida,
            mensagem_recebida=mensagem_recebida
        )
        
        return {"status": "Áudio de teste recebido e agendado para processamento."}

    except Exception as e:
        print(f"[API TEST CRITICAL] Erro inesperado no endpoint de teste de áudio: {e}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno no servidor.")


@app.post("/webhook/zapi/test-image", status_code=200, tags=["Testes"])
async def receber_imagem_para_teste(
    background_tasks: BackgroundTasks,
    phone: str = Form(...),
    image_file: UploadFile = File(...)
):
    """
    Endpoint de teste para simular o recebimento de uma mensagem de imagem via upload direto.
    """
    try:
        print(f"\n[API TEST] Imagem recebida para o telefone {phone} | Nome do arquivo: {image_file.filename}")

        # Lê os bytes do arquivo de imagem enviado
        image_bytes = await image_file.read()

        # Cria o DTO padronizado da aplicação
        mensagem_recebida = MensagemRecebida(
            telefone_remetente=phone,
            tipo="IMAGEM",
            media_conteudo=image_bytes,
            media_mime_type=image_file.content_type
        )
        
        # Delega para o mesmo serviço de aplicação
        background_tasks.add_task(
            servico_conversa.processar_mensagem_recebida,
            mensagem_recebida=mensagem_recebida
        )
        
        return {"status": "Imagem de teste recebida e agendada para processamento."}

    except Exception as e:
        print(f"[API TEST CRITICAL] Erro inesperado no endpoint de teste de imagem: {e}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno no servidor.")

