from abc import ABC, abstractmethod
from typing import Optional, List
from src.comunicacao_wpp_ia.dominio.modelos.responsavel import Responsavel

class RepositorioResponsavel(ABC):
    """
    Define a interface do repositório para operações relacionadas as pessoas.
    """    
    @abstractmethod
    def _buscar_responsaveis_do_produtor(self, base_url: str, id_produtor: str) -> List[Responsavel]:
        """
        Busca as pessoas cadastradas para um produtor
        """
        pass

    @abstractmethod
    def buscar_responsavel_por_telefone(self, base_url: str, id_produtor: str, telefone: str) -> Optional[Responsavel]:
        """
        Busca as pessoas cadastradas para um produtor com base no número de telefone.
        """
        pass