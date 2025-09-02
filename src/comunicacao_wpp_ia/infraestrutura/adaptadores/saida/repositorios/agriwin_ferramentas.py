from typing import List, Optional
from src.comunicacao_wpp_ia.dominio.modelos.produto import Produto
from src.comunicacao_wpp_ia.dominio.modelos.talhao import Talhao
from src.comunicacao_wpp_ia.dominio.modelos.propriedade import Propriedade
from src.comunicacao_wpp_ia.dominio.modelos.imobilizado import Imobilizado
from src.comunicacao_wpp_ia.dominio.modelos.ponto_estoque import PontoEstoque
from src.comunicacao_wpp_ia.dominio.modelos.safra import Safra
from src.comunicacao_wpp_ia.dominio.modelos.responsavel import Responsavel

from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_ferramentas import RepositorioFerramentas

from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.clientes_api.agriwin_cliente import AgriwinCliente


class RepoAgriwinFerramentas(RepositorioFerramentas):
    """
    Adaptador que implementa as interfaces de repositório utilizando a API do Agriwin.
    """
    def __init__(self, agriwin_cliente: AgriwinCliente):
        self._cliente = agriwin_cliente
        print("[INFRA] Adaptador do Repositório Agriwin inicializado.")

    def _processar_resposta(self, response, model):
        """Método auxiliar para processar a resposta JSON e converter para modelos Pydantic."""
        if response.status_code == 200:
            dados = response.json().get("dados", [])
            if isinstance(dados, list):
                return [model(**item) for item in dados]
            elif dados:
                return model(**dados)
        return None if isinstance(dados, dict) else []

    def buscar_produtos_do_produtor(self, id_produtor: int) -> List[Produto]:
        print(f"\n[API] Buscando todos os produtos para o produtor {id_produtor}...")
        endpoint = "/api/v1/produtos"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(endpoint, params=params)
        return self._processar_resposta(response, Produto)
    
    def buscar_produtos_em_estoque(self, id_produtor: int, produtos: List[str]) -> List[Produto]:
        print(f"\n[API] Buscando produtos em estoque para o produtor {id_produtor}...")
        endpoint = "/api/v1/estoque/produtos"
        ids_produtos = [p.id for p in produtos]
        params = {"identificador_produtor": id_produtor, "ids": ids_produtos}
        response = self._cliente.get(endpoint, params=params)
        return self._processar_resposta(response, Produto)

    def buscar_produtos_mais_consumidos(self, id_produtor: int, produtos: List[str]) -> List[Produto]:
        print(f"\n[API] Buscando consumo recente de produtos para o produtor {id_produtor}...")
        # TODO: preciso de uma rota para buscar consumos filtrando periodo (obrigatoriamente) e lista de produtos (opcional)
        endpoint = "/api/v1/consumo/produtos/mais-consumidos"
        ids_produtos = [p.id for p in produtos]
        params = {"identificador_produtor": id_produtor, "ids": ids_produtos}
        response = self._cliente.get(endpoint, params=params)
        return self._processar_resposta(response, Produto)

    def buscar_talhoes_do_produtor(self, id_produtor: int) -> List[Talhao]:
        print(f"\n[API] Buscando todos os talhões para o produtor {id_produtor}...")
        endpoint = "/api/v1/plantios"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(endpoint, params=params)
        return self._processar_resposta(response, Talhao)
    
    def buscar_propriedades_do_produtor(self, id_produtor: int) -> List[Propriedade]:
        print(f"\n[API] Buscando todas as propriedades para o produtor {id_produtor}...")
        endpoint = "/api/v1/plantios"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(endpoint, params=params)
        return self._processar_resposta(response, Propriedade)
    
    def buscar_maquinas_do_produtor(self, id_produtor: int) -> List[Imobilizado]:
        print(f"\n[API] Buscando todas as máquinas para o produtor {id_produtor}...")
        # TODO: Alterar rotas para "maquinas" "implementos" "benfeitorias"...
        endpoint = "/api/v1/imobilizados"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(endpoint, params=params)
        return self._processar_resposta(response, Imobilizado)
    
    def buscar_pontos_estoque_do_produtor(self, id_produtor: int) -> List[PontoEstoque]:
        print(f"\n[API] Buscando pontos de estoque para o produtor {id_produtor}...")
        endpoint = "/api/v1/estoques"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(endpoint, params=params)
        return self._processar_resposta(response, PontoEstoque)
    
    def buscar_safras_do_produtor(self, id_produtor: int) -> List[Safra]:
        print(f"\n[API] Buscando safras para o produtor {id_produtor}...")
        endpoint = "/api/v1/safras"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(endpoint, params=params)
        return self._processar_resposta(response, Safra)
    
    def _buscar_responsaveis_do_produtor(self, id_produtor: int) -> List[Responsavel]:
        print(f"\n[API] Buscando responsáveis para o produtor {id_produtor}...")
        endpoint = "/api/v1/pessoas"
        params = {"identificador_produtor": id_produtor}
        response = self._cliente.get(endpoint, params=params)
        # return self._processar_resposta(response, Responsavel)
    
        responsavel_data = [
            {"identificador": 601, "nome": "João da Silva", "telefone": "+5511988882222", "nome_fantasia": ""},
            {"identificador": 602, "nome": "Maria Oliveira", "telefone": "+5541999991111", "nome_fantasia": ""},
        ]
        return [Responsavel(**data) for data in responsavel_data]

    
    def buscar_responsavel_por_telefone(self, id_produtor: int, telefone: str) -> Optional[Responsavel]:
        print(f"\nBuscando responsável pelo telefone {telefone} para o produtor {id_produtor}...")
        responsaveis = self._buscar_responsaveis_do_produtor(id_produtor)
        for responsavel in responsaveis:
            if responsavel.telefone == telefone:
                return responsavel
        return None
    