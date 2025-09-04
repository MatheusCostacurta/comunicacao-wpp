from src.comunicacao_wpp_ia.dominio.modelos.dados_remetente import DadosRemetente
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_remetente import RepositorioRemetente

class ObterRemetente:
    def __init__(self, repo_remetente: RepositorioRemetente):
        self._repo_remetente = repo_remetente

    def executar(self, telefone: str) -> DadosRemetente:
        remetente = self._repo_remetente.buscar_remetente_por_telefone(telefone)
        if not remetente:
            print(f"[ERROR] Não foi possível encontrar um produtor associado ao número {telefone}.")
            return None
        return remetente