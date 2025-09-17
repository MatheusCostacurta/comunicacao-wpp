from typing import List, Optional, Any, Callable, Type
from pydantic import ValidationError, BaseModel
import requests

# --- DTOs da Camada de Infraestrutura ---
from src.comunicacao_wpp_ia.infraestrutura.dtos.agriwin_dtos import (
    ProdutoAgriwinDTO,
    AreasAgriwinDTO,
    MaquinaAgriwinDTO,
    PontoEstoqueAgriwinDTO,
    SafraAgriwinDTO,
    ResponsavelAgriwinDTO
)
# --- Mapeador da Camada de Infraestrutura ---
from src.comunicacao_wpp_ia.infraestrutura.dtos.agriwin_mapeador import AgriwinMapeador

# --- Modelos e Portas do Domínio ---
from src.comunicacao_wpp_ia.dominio.modelos.produto import Produto
from src.comunicacao_wpp_ia.dominio.modelos.talhao import Talhao
from src.comunicacao_wpp_ia.dominio.modelos.propriedade import Propriedade
from src.comunicacao_wpp_ia.dominio.modelos.imobilizado import Imobilizado
from src.comunicacao_wpp_ia.dominio.modelos.ponto_estoque import PontoEstoque
from src.comunicacao_wpp_ia.dominio.modelos.safra import Safra
from src.comunicacao_wpp_ia.dominio.modelos.responsavel import Responsavel
from src.comunicacao_wpp_ia.dominio.modelos.plantio import Plantio
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_ferramentas import RepositorioFerramentas

# --- Cliente HTTP ---
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.clientes_api.agriwin_cliente import AgriwinCliente

class RepoAgriwinFerramentas(RepositorioFerramentas):
    """
    Adaptador que implementa as interfaces de repositório utilizando a API do Agriwin.
    Utiliza DTOs para validar a estrutura dos dados da API e um Mapeador para traduzi-los em objetos de domínio, protegendo o núcleo da aplicação.
    """
    def __init__(self, agriwin_cliente: AgriwinCliente):
        self._cliente = agriwin_cliente
        print("[INFRA] Adaptador do Repositório Agriwin inicializado.")

    def _processar_e_mapear_resposta(self, response: requests.Response, dto_class: Type[BaseModel], map_func: Callable[[Any], Any]) -> List[Any]:
        """
        Método genérico e robusto para processar a resposta da API.
        1. Valida os dados brutos contra um DTO.
        2. Usa uma função de mapeamento para converter o DTO em um objeto de domínio.
        """
        if response.status_code != 200:
            return []

        dados_api = response.json().get("dados", [])
        if not isinstance(dados_api, list):
            dados_api = [dados_api] if dados_api else []

        objetos_dominio = []
        for item_dict in dados_api:
            try:
                #TODO: Não esta legal esses if/else para um método genérico
                if dto_class == ProdutoAgriwinDTO:
                    if 'ingredientes_ativo' in item_dict and isinstance(item_dict['ingredientes_ativo'], list):
                        item_dict['ingredientes_ativo'] = [{'nome': ia} for ia in item_dict['ingredientes_ativo'] if isinstance(ia, str)]
                    
                    if 'unidades_medida' in item_dict and isinstance(item_dict['unidades_medida'], list):
                        item_dict['unidades_medida'] = [{'sigla': um} for um in item_dict['unidades_medida'] if isinstance(um, str)]

                dto_instance = dto_class.model_validate(item_dict)
                domain_object = map_func(dto_instance)
                objetos_dominio.append(domain_object)
            except ValidationError as e:
                print(f"[ADAPTER WARNING] Dados da API para '{dto_class.__name__}' são inválidos e serão ignorados. Erro: {e}")
            except Exception as e:
                print(f"[ADAPTER CRITICAL] Erro inesperado durante o mapeamento de '{dto_class.__name__}'. Erro: {e}")

        return objetos_dominio

    def buscar_produtos_do_produtor(self, base_url: str, id_produtor: str) -> List[Produto]:
        print(f"\n[API] Buscando todos os produtos para o produtor {id_produtor}...")
        endpoint = "/api/v1/produtos"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(base_url, endpoint, params=params)
        return self._processar_e_mapear_resposta(response, ProdutoAgriwinDTO, AgriwinMapeador.para_produto_dominio)
    
    def buscar_produtos_em_estoque(self, base_url: str, id_produtor: str, produtos: List[str]) -> List[Produto]:
        print(f"\n[API] Buscando produtos em estoque para o produtor {id_produtor}...")
        endpoint = "/api/v1/estoque/produtos"
        ids_produtos = [p.id for p in produtos]
        params = {"identificador_produtor": id_produtor, "ids": ids_produtos}
        response = self._cliente.get(base_url, endpoint, params=params)
        return self._processar_e_mapear_resposta(response, ProdutoAgriwinDTO, AgriwinMapeador.para_produto_dominio)

    def buscar_produtos_mais_consumidos(self, base_url: str, id_produtor: str, produtos: List[str]) -> List[Produto]:
        print(f"\n[API] Buscando consumo recente de produtos para o produtor {id_produtor}...")
        # TODO: preciso de uma rota para buscar consumos filtrando periodo (obrigatoriamente) e lista de produtos (opcional)
        endpoint = "/api/v1/consumos/produtos/mais-consumidos"
        ids_produtos = [p.id for p in produtos]
        params = {"identificador_produtor": id_produtor, "ids": ids_produtos}
        response = self._cliente.get(base_url, endpoint, params=params)
        return self._processar_e_mapear_resposta(response, ProdutoAgriwinDTO, AgriwinMapeador.para_produto_dominio)

    def buscar_atraves_dos_talhoes_do_produtor(self, base_url: str, id_produtor: str) -> List[Talhao]:
        print(f"\n[API] Buscando todos os talhões para o produtor {id_produtor}...")
        endpoint = "/api/v1/areas"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(base_url, endpoint, params=params)
        return self._processar_e_mapear_resposta(response, AreasAgriwinDTO, AgriwinMapeador.para_plantio_dominio)
    
    def buscar_propriedades_do_produtor(self, base_url: str, id_produtor: str) -> List[Propriedade]:
        print(f"\n[API] Buscando todas as propriedades para o produtor {id_produtor}...")
        endpoint = "/api/v1/areas"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(base_url, endpoint, params=params)
        return self._processar_e_mapear_resposta(response, AreasAgriwinDTO, AgriwinMapeador.para_propriedade_dominio)
    
    def buscar_plantios_do_produtor(self, base_url: str, id_produtor: str) -> List[Plantio]:
        print(f"\n[API] Buscando todos os plantios para o produtor {id_produtor}...")
        endpoint = "/api/v1/areas"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(base_url, endpoint, params=params)
        return self._processar_e_mapear_resposta(response, AreasAgriwinDTO, AgriwinMapeador.para_plantio_dominio)
    
    def buscar_maquinas_do_produtor(self, base_url: str, id_produtor: str) -> List[Imobilizado]:
        print(f"\n[API] Buscando todas as máquinas para o produtor {id_produtor}...")
        endpoint = "/api/v1/maquinas"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(base_url, endpoint, params=params)
        return self._processar_e_mapear_resposta(response, MaquinaAgriwinDTO, AgriwinMapeador.para_imobilizado_dominio)
    
    def buscar_pontos_estoque_do_produtor(self, base_url: str, id_produtor: str) -> List[PontoEstoque]:
        print(f"\n[API] Buscando pontos de estoque para o produtor {id_produtor}...")
        endpoint = "/api/v1/estoques/locais"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(base_url, endpoint, params=params)
        return self._processar_e_mapear_resposta(response, PontoEstoqueAgriwinDTO, AgriwinMapeador.para_ponto_estoque_dominio)
       
    def buscar_safras_do_produtor(self, base_url: str, id_produtor: str) -> List[Safra]:
        print(f"\n[API] Buscando safras para o produtor {id_produtor}...")
        endpoint = "/api/v1/safras"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(base_url, endpoint, params=params)
        return self._processar_e_mapear_resposta(response, SafraAgriwinDTO, AgriwinMapeador.para_safra_dominio)
    
    def _buscar_responsaveis_do_produtor(self, base_url: str, id_produtor: str) -> List[Responsavel]:
        print(f"\n[API] Buscando responsáveis para o produtor {id_produtor}...")
        endpoint = "/api/v1/pessoas"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(base_url, endpoint, params=params)
        return self._processar_e_mapear_resposta(response, ResponsavelAgriwinDTO, AgriwinMapeador.para_responsavel_dominio)

    
    def buscar_responsavel_por_telefone(self, base_url: str, id_produtor: str, telefone: str) -> Optional[Responsavel]:
        print(f"\nBuscando responsável pelo telefone {telefone} para o produtor {id_produtor}...")
        responsaveis = self._buscar_responsaveis_do_produtor(base_url, id_produtor)
        for responsavel in responsaveis:
            if responsavel.telefone == telefone:
                return responsavel
        return None
    