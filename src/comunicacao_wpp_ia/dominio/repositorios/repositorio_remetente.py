from abc import ABC, abstractmethod
from typing import Optional
from src.comunicacao_wpp_ia.aplicacao.dtos.dados_remetente import DadosRemetente

class RepositorioRemetente(ABC):
    """
    Define a interface do repositório para operações relacionadas a remetentes.
    """
    @abstractmethod
    def buscar_remetente_por_telefone(self, telefone: str) -> Optional[DadosRemetente]:
        """
        Busca os dados de um remetente (produtor) com base no número de telefone.
        """
        pass