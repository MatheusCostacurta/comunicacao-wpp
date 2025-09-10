from typing import Optional
from src.comunicacao_wpp_ia.dominio.modelos.dados_remetente import DadosRemetente
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_remetente import RepositorioRemetente

from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.clientes_api.agriwin_cliente import AgriwinCliente


class RepoAgriwinRemetente(RepositorioRemetente):
    """
    Adaptador que implementa as interfaces de repositório para o remetente.
    """

    def __init__(self, agriwin_cliente: AgriwinCliente):
        self._cliente = agriwin_cliente
        print("[INFRA] Adaptador do Repositório AgriwinRemetente inicializado.")
    
    def buscar_remetente_por_telefone(self, telefone: str) -> Optional[DadosRemetente]:
        """
        Busca na API da Agriwin a lista de produtores para um dado responsável.
        """

        # endpoint = "/api/v1/produtores"
        # params = {"telefone": telefone}
        # response = self._cliente.get(endpoint, params=params)
        return DadosRemetente(produtor_id=["NTc="], numero_telefone=telefone)