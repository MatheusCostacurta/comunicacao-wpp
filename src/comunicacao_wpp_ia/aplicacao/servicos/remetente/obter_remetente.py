from src.comunicacao_wpp_ia.dominio.modelos.dados_remetente import DadosRemetente
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_remetente import RepositorioRemetente
from src.comunicacao_wpp_ia.dominio.excecoes.excecoes import MultiplosProdutoresError, NenhumProdutorEncontradoError

class ObterRemetente:
    def __init__(self, repo_remetente: RepositorioRemetente):
        self._repo_remetente = repo_remetente

    def executar(self, telefone: str) -> DadosRemetente:
        remetente = self._repo_remetente.buscar_remetente_por_telefone(telefone)
        if not remetente:
            # Você pode querer criar uma exceção para remetente não encontrado também
            print(f"[ERROR] Não foi possível encontrar um produtor associado ao número {telefone}.")
            raise ValueError("Remetente não encontrado.")
        
        produtores = remetente.produtor_id 
        if len(produtores) > 1:
            # Regra de negócio: se tiver mais de 1, lança exceção
            raise MultiplosProdutoresError("O usuário está associado a mais de um produtor.")
        
        if len(produtores) == 0:
            # Regra de negócio: se não tiver nenhum, lança exceção
            raise NenhumProdutorEncontradoError("O usuário não está associado a nenhum produtor.")

        return remetente