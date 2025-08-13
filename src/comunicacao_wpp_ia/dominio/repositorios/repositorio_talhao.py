from abc import ABC, abstractmethod
from typing import List
from src.comunicacao_wpp_ia.dominio.modelos.talhao import Talhao

class RepositorioTalhao(ABC):
    """
    Define a interface do repositório para operações relacionadas a talhoes.
    O domínio e a aplicação dependem desta abstração.
    """
    @abstractmethod
    def buscar_talhoes_do_produtor(self, id_produtor: int) -> List[Talhao]:
        pass