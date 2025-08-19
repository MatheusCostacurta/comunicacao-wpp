from abc import ABC, abstractmethod
from typing import Dict, Any
from src.comunicacao_wpp_ia.aplicacao.dtos.mensagem_recebida import MensagemRecebida

class Whatsapp(ABC):
    """
    Define a interface (Porta) para um serviço de comunicação com o wpp.
    A camada de aplicação dependerá desta abstração para enviar e receber mensagens.
    """

    @abstractmethod
    def enviar(self, telefone: str, mensagem: str) -> None:
        """
        Envia uma mensagem de texto para um número de telefone específico.
        """
        pass

    @abstractmethod
    def receber(self, payload_webhook: Dict[str, Any]) -> MensagemRecebida:
        """
        Interpreta o payload de um webhook de entrada, valida e o converte
        para um DTO padronizado da aplicação (MensagemRecebida).
        """
        pass