from typing import Optional
from src.comunicacao_wpp_ia.dominio.modelos.dados_remetente import DadosRemetente
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_remetente import RepositorioRemetente
from src.comunicacao_wpp_ia.infraestrutura.dtos.agriwin_dtos import RemetenteAgriwinDTO
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.clientes_api.agriwin_cliente import AgriwinCliente
from pydantic import ValidationError

class RepoAgriwinRemetente(RepositorioRemetente):
    """
    Adaptador que implementa as interfaces de repositório para o remetente.
    """

    def __init__(self, agriwin_cliente: AgriwinCliente):
        self._cliente = agriwin_cliente
        print("[INFRA] Adaptador do Repositório AgriwinRemetente inicializado.")
    
    # TODO: Precisa melhorar esse método
    def buscar_remetente_por_telefone(self, telefone: str) -> Optional[DadosRemetente]:
        """
        Busca na API da Agriwin a lista de produtores para um dado responsável.
        """
        endpoint = "/api/v1/produtores"
        params = {"telefone": telefone}
        dados_api = []
        base_correta = None
        for base_url in self._cliente.todas_bases_urls:
            response = self._cliente.get(base_url, endpoint, params=params)
            if response.status_code == 200:
                dados_api = response.json().get("dados", [])
            if dados_api:
                base_correta = base_url
                break
        
        if dados_api == []:
            return None
        
        remetente = DadosRemetente(
            base_url=base_correta,
            numero_telefone=telefone
        )
        for item in dados_api:
            try:
                dto_instance = RemetenteAgriwinDTO.model_validate(item)
                remetente.produtor_id.append(dto_instance.identificador)
            except ValidationError as e:
                print(f"[ADAPTER WARNING] Item de remetente inválido ignorado. Erro: {e}")
            
        return remetente