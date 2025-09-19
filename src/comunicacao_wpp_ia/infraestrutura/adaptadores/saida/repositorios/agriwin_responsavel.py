from typing import List, Optional, Any, Callable, Type
from pydantic import ValidationError, BaseModel
import requests
from src.comunicacao_wpp_ia.dominio.modelos.responsavel import Responsavel
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_responsavel import RepositorioResponsavel
from src.comunicacao_wpp_ia.infraestrutura.dtos.agriwin_dtos import PessoaAgriwinDTO
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.clientes_api.agriwin_cliente import AgriwinCliente
from src.comunicacao_wpp_ia.infraestrutura.dtos.agriwin_mapeador import AgriwinMapeador

class RepoAgriwinResponsavel(RepositorioResponsavel):
    """
    Adaptador que implementa as interfaces de repositório para o responsavel.
    """

    def __init__(self, agriwin_cliente: AgriwinCliente):
        self._cliente = agriwin_cliente
        print("[INFRA] Adaptador do Repositório AgriwinRemetente inicializado.")
    
    # TODO: criar uma classe para esses 2 metodos que serão usados em varios lugares
    def _processar_resposta(self, response: requests.Response) -> List[Any]:
        if response.status_code != 200:
            return []

        dados_api = response.json().get("dados", [])
        if not isinstance(dados_api, list):
            dados_api = [dados_api] if dados_api else []
        
        return dados_api
    
    def _processar_e_mapear_resposta(self, response: requests.Response, dto_class: Type[BaseModel], map_func: Callable[[Any], Any]) -> List[Any]:
        """
        Método genérico e robusto para processar a resposta da API.
        1. Valida os dados brutos contra um DTO.
        2. Usa uma função de mapeamento para converter o DTO em um objeto de domínio.
        """
        dados_api = self._processar_resposta(response)

        objetos_dominio = []
        for item_dict in dados_api:
            try:
                dto_instance = dto_class.model_validate(item_dict)
                domain_object = map_func(dto_instance)
                objetos_dominio.append(domain_object)
            except ValidationError as e:
                print(f"[ADAPTER WARNING] Dados da API para '{dto_class.__name__}' são inválidos e serão ignorados. Erro: {e}")
            except Exception as e:
                print(f"[ADAPTER CRITICAL] Erro inesperado durante o mapeamento de '{dto_class.__name__}'. Erro: {e}")

        return objetos_dominio
    
    def _buscar_responsaveis_do_produtor(self, base_url: str, id_produtor: str) -> List[Responsavel]:
        print(f"\n[API] Buscando responsáveis para o produtor {id_produtor}...")
        endpoint = "/api/v1/pessoas"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(base_url, endpoint, params=params)
        return self._processar_e_mapear_resposta(response, PessoaAgriwinDTO, AgriwinMapeador.para_responsavel_dominio)

    
    def buscar_responsavel_por_telefone(self, base_url: str, id_produtor: str, telefone: str) -> Optional[Responsavel]:
        print(f"\nBuscando responsável pelo telefone {telefone} para o produtor {id_produtor}...")
        responsaveis = self._buscar_responsaveis_do_produtor(base_url, id_produtor)
        for responsavel in responsaveis:
            if responsavel.telefone == telefone:
                return responsavel
        return None