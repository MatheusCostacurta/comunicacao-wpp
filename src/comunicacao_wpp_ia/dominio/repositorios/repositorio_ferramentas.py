from abc import ABC, abstractmethod
from typing import List, Optional
from src.comunicacao_wpp_ia.dominio.modelos.imobilizado import Imobilizado
from src.comunicacao_wpp_ia.dominio.modelos.safra import Safra
from src.comunicacao_wpp_ia.dominio.modelos.responsavel import Responsavel
from src.comunicacao_wpp_ia.dominio.modelos.produto import Produto
from src.comunicacao_wpp_ia.dominio.modelos.ponto_estoque import PontoEstoque
from src.comunicacao_wpp_ia.dominio.modelos.talhao import Talhao
from src.comunicacao_wpp_ia.dominio.modelos.propriedade import Propriedade

class RepositorioFerramentas(ABC):
    """
    Define a interface do repositório para operações relacionadas a llm.
    """
    @abstractmethod
    def buscar_maquinas_do_produtor(self, id_produtor: int) -> List[Imobilizado]:
        pass

    @abstractmethod
    def buscar_pontos_estoque_do_produtor(self, id_produtor: int) -> List[PontoEstoque]:
        pass

    @abstractmethod
    def buscar_produtos_do_produtor(self, id_produtor: int) -> List[Produto]:
        pass

    @abstractmethod
    def buscar_produtos_em_estoque(self, id_produtor: int, nomes_produtos: List[str]) -> List[Produto]:
        pass
    
    @abstractmethod
    def buscar_produtos_mais_consumidos(self, id_produtor: int, nomes_produtos: List[str]) -> List[Produto]:
        pass

    @abstractmethod
    def buscar_responsavel_por_telefone(self, id_produtor: int, telefone: str) -> Optional[Responsavel]:
        pass

    @abstractmethod
    def buscar_safras_do_produtor(self, id_produtor: int) -> List[Safra]:
        pass

    @abstractmethod
    def buscar_talhoes_do_produtor(self, id_produtor: int) -> List[Talhao]:
        pass
    
    @abstractmethod
    def buscar_propriedades_do_produtor(self, id_produtor: int) -> List[Propriedade]:
        pass