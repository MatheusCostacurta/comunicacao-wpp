from typing import Optional
from src.comunicacao_wpp_ia.dominio.modelos.dados_remetente import DadosRemetente
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_remetente import RepositorioRemetente


class RepoAgriwinRemetente(RepositorioRemetente):
    """
    Adaptador que implementa as interfaces de repositório para o remetente.
    """
    def __init__(self):
        print("[INFRA] Adaptador do Repositório AgriwinRemetente inicializado.")
    
    def buscar_remetente_por_telefone(self, telefone: str) -> Optional[DadosRemetente]:
        print(f"\n[API MOCK] Buscando produtor pelo telefone {telefone}...")
        return DadosRemetente(produtor_id=1, numero_telefone=telefone)