from abc import ABC, abstractmethod
from typing import Dict, Tuple
from src.comunicacao_wpp_ia.dominio.modelos.consumo import Consumo

class RepositorioConsumo(ABC):
    @abstractmethod
    def salvar_consumo(self, dados_consumo: Dict) -> Tuple[int, Dict]:
        pass