from typing import Optional
from src.comunicacao_wpp_ia.dominio.modelos.responsavel import Responsavel

class LocalizarResponsavelService:
    def __init__(self, api_ferramentas):
        self.api = api_ferramentas

    def obter(self, telefone: str, id_produtor: int) -> Optional[Responsavel]:
        """Busca um responsável pelo número de telefone."""
        print(f"\n[SERVICE] Buscando responsável pelo telefone: {telefone}")
        responsavel = self.api.buscar_responsavel_por_telefone(id_produtor=id_produtor, telefone=telefone)
        if responsavel:
            print(f"[SERVICE] Responsável encontrado: {responsavel.nome}")
        else:
            print("[SERVICE] Nenhum responsável encontrado para este telefone.")
        return responsavel