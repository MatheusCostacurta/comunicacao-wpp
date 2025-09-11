from typing import List, Optional
from thefuzz import process
from src.comunicacao_wpp_ia.dominio.modelos.propriedade import Propriedade

class LocalizarPropriedadeService:
    def __init__(self, api_ferramentas):
        self.api = api_ferramentas

    def obter(self, base_url: str, id_produtor: int) -> List[Propriedade]:
        """Encontra as propriedades mais prováveis com base nos nomes mencionados."""
        todas_propriedades = self.api.buscar_propriedades_do_produtor(base_url, id_produtor)
        if not todas_propriedades:
            return []

        return todas_propriedades