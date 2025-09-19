from typing import Optional
from src.comunicacao_wpp_ia.dominio.modelos.responsavel import Responsavel
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_responsavel import RepositorioResponsavel

class ObterResponsavel:
    def __init__(self, repo_responsavel: RepositorioResponsavel):
        self._repo_responsavel = repo_responsavel
    
    def obter(self, base_url: str, telefone: str, id_produtor: int) -> Optional[Responsavel]:
        """Busca um responsável pelo número de telefone."""
        print(f"\n[SERVICE] Buscando responsável pelo telefone: {telefone}")
        responsavel = self._repo_responsavel.buscar_responsavel_por_telefone(base_url=base_url, id_produtor=id_produtor, telefone=telefone)
        if responsavel:
            print(f"[SERVICE] Responsável encontrado: {responsavel.nome}")
        else:
            print("[SERVICE] Nenhum responsável encontrado para este telefone.")

        return responsavel