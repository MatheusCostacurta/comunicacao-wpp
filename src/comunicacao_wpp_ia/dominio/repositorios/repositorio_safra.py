from abc import ABC, abstractmethod
from typing import List
from src.comunicacao_wpp_ia.dominio.modelos.safra import Safra

class RepositorioSafra(ABC):
    @abstractmethod
    def buscar_safras_do_produtor(self, id_produtor: int) -> List[Safra]:
        pass