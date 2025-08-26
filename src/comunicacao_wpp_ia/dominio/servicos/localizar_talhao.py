from typing import List, Optional
from thefuzz import process
from src.comunicacao_wpp_ia.dominio.modelos.talhao import Talhao

class LocalizarTalhaoService:
    def __init__(self, api_ferramentas):
        self.api = api_ferramentas

    def obter(self, id_produtor: int) -> List[Talhao]:
        """Encontra os talhões mais prováveis com base nos nomes mencionados."""
        todos_talhoes = self.api.buscar_talhoes_do_produtor(id_produtor)

        if not todos_talhoes:
            return []
            
        return todos_talhoes