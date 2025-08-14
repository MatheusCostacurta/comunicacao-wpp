from abc import ABC, abstractmethod
from typing import Dict, List, Any

class ServicoMemoria(ABC):
    """
    Define a interface (Porta) para um serviço de gerenciamento de memória de conversa.
    A camada de aplicação dependerá desta abstração.
    """

    @abstractmethod
    def obter_estado(self, chave_identificadora: str) -> Dict[str, Any]:
        """
        Obtém o estado atual da conversa com base em uma chave identificadora (ex: número de telefone).
        """
        pass

    @abstractmethod
    def salvar_estado(self, chave_identificadora: str, historico: List[Any]):
        """
        Salva o estado atualizado da conversa.
        """
        pass

    @abstractmethod
    def limpar_memoria_conversa(self, chave_identificadora: str):
        """
        Remove o estado de uma conversa da memória.
        """
        pass