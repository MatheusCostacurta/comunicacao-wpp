from typing import Optional
from thefuzz import process
from src.comunicacao_wpp_ia.dominio.modelos.imobilizado import Imobilizado

class LocalizarMaquinaService:
    def __init__(self, api_ferramentas):
        self.api = api_ferramentas

    def obter(self, id_produtor: int) -> Optional[Imobilizado]:
        """Encontra a máquina mais provável com base no nome."""
        todas_maquinas = self.api.buscar_maquinas_do_produtor(id_produtor)

        if not todas_maquinas:
            return None

        return todas_maquinas