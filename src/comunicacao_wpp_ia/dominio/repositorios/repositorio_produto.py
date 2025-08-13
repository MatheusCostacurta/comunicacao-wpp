from abc import ABC, abstractmethod
from typing import List
from src.comunicacao_wpp_ia.dominio.modelos.produto import Produto

class RepositorioProduto(ABC):
    """
    Define a interface do repositório para operações relacionadas a produtos.
    O domínio e a aplicação dependem desta abstração.
    """
    @abstractmethod
    def buscar_produtos_do_produtor(self, id_produtor: int) -> List[Produto]:
        pass

    @abstractmethod
    def buscar_produtos_em_estoque(self, id_produtor: int, nomes_produtos: List[str]) -> List[Produto]:
        pass
    
    @abstractmethod
    def buscar_produtos_mais_consumidos(self, id_produtor: int, nomes_produtos: List[str]) -> List[Produto]:
        pass