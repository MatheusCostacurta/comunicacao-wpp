from abc import ABC, abstractmethod
from typing import List
from src.comunicacao_wpp_ia.dominio.modelos.ponto_estoque import PontoEstoque

class RepositorioPontoEstoque(ABC):
    @abstractmethod
    def buscar_pontos_estoque_do_produtor(self, id_produtor: int) -> List[PontoEstoque]:
        pass