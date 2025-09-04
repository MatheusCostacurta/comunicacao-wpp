from abc import ABC, abstractmethod
from typing import Dict, Tuple

class RepositorioConsumo(ABC):
    @abstractmethod
    def salvar(self, dados_consumo: Dict) -> Tuple[int, Dict]:
        pass