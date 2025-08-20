from src.comunicacao_wpp_ia.aplicacao.dtos.mensagem_recebida import MensagemRecebida
from src.comunicacao_wpp_ia.aplicacao.portas.pre_processamento_texto import ServicoPreProcessamento
from src.comunicacao_wpp_ia.aplicacao.portas.transcrever_audio import ServicoTranscricao
from src.comunicacao_wpp_ia.aplicacao.portas.extrair_imagem import ServicoImagem

class PreProcessamentoService(ServicoPreProcessamento):
    """
    Serviço de aplicação que orquestra a conversão de diferentes tipos de mídia em texto.
    """
    def __init__(self, servico_transcricao: ServicoTranscricao, servico_imagem: ServicoImagem):
        self._servico_transcricao = servico_transcricao
        self._servico_imagem = servico_imagem

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
            return self._servico_imagem.extrair_texto_de_imagem(mensagem.media_conteudo)
        
        print(f"[PRE-PROCESSAMENTO] Tipo de mensagem '{mensagem.tipo}' não suportado para pré-processamento.")
        return ""