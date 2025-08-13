from abc import ABC, abstractmethod
from typing import List
from src.comunicacao_wpp_ia.dominio.modelos.imobilizado import Imobilizado

class RepositorioImobilizado(ABC):
    """
    Define a interface do repositório para operações relacionadas a imobilizados.
    O domínio e a aplicação dependem desta abstração.
    """
    @abstractmethod
    def buscar_maquinas_do_produtor(self, id_produtor: int) -> List[Imobilizado]:
        pass