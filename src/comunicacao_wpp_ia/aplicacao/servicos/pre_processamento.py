from src.comunicacao_wpp_ia.aplicacao.dtos.mensagem_recebida import MensagemRecebida
from src.comunicacao_wpp_ia.aplicacao.portas.pre_processamento_texto import ServicoPreProcessamento
from src.comunicacao_wpp_ia.aplicacao.portas.transcrever_audio import ServicoTranscricao
from src.comunicacao_wpp_ia.aplicacao.portas.extrair_texto_imagem import ExtrairTextoDaImagem

class PreProcessamentoService(ServicoPreProcessamento):
    """
    Serviço de aplicação que orquestra a conversão de diferentes tipos de mídia em texto.
    """
    def __init__(self, servico_transcricao: ServicoTranscricao, extrair_texto_imagem: ExtrairTextoDaImagem):
        self._servico_transcricao = servico_transcricao
        self._extrair_texto_imagem = extrair_texto_imagem

    def processar(self, mensagem: MensagemRecebida) -> str:
        """
        Verifica o tipo da mensagem e delega para o serviço correspondente.
        Retorna sempre uma string de texto.
        """
        print(f"\n--- INICIANDO PRÉ-PROCESSAMENTO (TIPO: {mensagem.tipo}) ---")
        if mensagem.tipo == "TEXTO":
            return mensagem.texto_conteudo or ""
        
        if mensagem.tipo == "AUDIO":
            if not mensagem.media_conteudo:
                print("[PRE-PROCESSAMENTO] Erro: Mensagem de áudio sem conteúdo.")
                return ""
            return self._servico_transcricao.transcrever(mensagem.media_conteudo)

        if mensagem.tipo == "IMAGEM":
            if not mensagem.media_conteudo:
                print("[PRE-PROCESSAMENTO] Erro: Mensagem de imagem sem conteúdo.")
                return ""
            return self._extrair_texto_imagem.executar(mensagem.media_conteudo)
        
        print(f"[PRE-PROCESSAMENTO] Tipo de mensagem '{mensagem.tipo}' não suportado para pré-processamento.")
        return ""