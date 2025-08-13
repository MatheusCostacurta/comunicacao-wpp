from abc import ABC, abstractmethod
from typing import Dict, Any

class AgenteComFerramentas(ABC):
    """
    Define a interface (Porta) para um agente executável.
    A aplicação usará este contrato para executar qualquer agente, independentemente de como ele foi construído.
    """

    @abstractmethod
    def executar(self, entradas: Dict[str, Any]) -> str:
        """
        Executa o agente com um dicionário de entradas e retorna a saída final como string.
        """
        pass