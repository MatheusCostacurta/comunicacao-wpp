from abc import ABC, abstractmethod
from typing import List, Optional
from src.comunicacao_wpp_ia.dominio.modelos.responsavel import Responsavel

class RepositorioResponsavel(ABC):
    @abstractmethod
    def buscar_responsaveis_do_produtor(self, id_produtor: int) -> List[Responsavel]:
        pass

    @abstractmethod
    def buscar_responsavel_por_telefone(self, id_produtor: int, telefone: str) -> Optional[Responsavel]:
        pass