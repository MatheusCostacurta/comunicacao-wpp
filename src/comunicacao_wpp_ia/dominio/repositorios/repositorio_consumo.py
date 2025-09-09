from abc import ABC, abstractmethod
from typing import Dict, Tuple
from src.comunicacao_wpp_ia.aplicacao.dtos.resposta_api import RespostaApi

class RepositorioConsumo(ABC):
    @abstractmethod
    def salvar(self, dados_consumo: Dict) -> Tuple[int, RespostaApi]:
        pass