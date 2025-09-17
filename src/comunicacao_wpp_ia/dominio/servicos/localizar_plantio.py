from typing import List
from thefuzz import process
from src.comunicacao_wpp_ia.dominio.modelos.plantio import Plantio

class LocalizarPlantioService:
    def __init__(self, api_ferramentas):
        self.api = api_ferramentas

    def obter(self, base_url: str, id_produtor: int) -> List[Plantio]:
        """Encontra os plantios mais prováveis com base nos nomes mencionados."""
        todos_plantios = self.api.buscar_plantios_do_produtor(base_url, id_produtor)

        if not todos_plantios:
            return []
            
        return todos_plantios