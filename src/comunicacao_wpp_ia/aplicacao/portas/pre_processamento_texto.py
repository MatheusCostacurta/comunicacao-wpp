from abc import ABC, abstractmethod
from src.comunicacao_wpp_ia.aplicacao.dtos.mensagem_recebida import MensagemRecebida

class ServicoPreProcessamento(ABC):
    """
    Define a interface (Porta) para o serviço que orquestra o pré-processamento
    de mensagens recebidas, convertendo-as para texto.
    """

    @abstractmethod
    def processar(self, mensagem: MensagemRecebida) -> str:
        """
        Processa uma mensagem recebida e retorna seu conteúdo textual.
        """
        pass