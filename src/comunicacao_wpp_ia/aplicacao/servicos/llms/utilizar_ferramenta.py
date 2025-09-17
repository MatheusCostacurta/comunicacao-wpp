import json
from datetime import date
from typing import List, Dict, Any, Optional

from src.comunicacao_wpp_ia.aplicacao.portas.ferramentas import Ferramentas
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_ferramentas import RepositorioFerramentas
from src.comunicacao_wpp_ia.dominio.servicos.localizar_produto import LocalizarProdutoService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_talhao import LocalizarTalhaoService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_plantio import LocalizarPlantioService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_propriedade import LocalizarPropriedadeService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_maquina import LocalizarMaquinaService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_ponto_estoque import LocalizarPontoEstoqueService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_safra import LocalizarSafraService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_responsavel import LocalizarResponsavelService

class UtilizarFerramenta(Ferramentas):
    """
    Esta classe contém a lógica de negócio real de cada ferramenta, orquestrando os serviços de domínio para obter os dados necessários.
    """
    def __init__(self, repositorio_ferramentas: RepositorioFerramentas):
        """
        Inicializa o serviço de ferramentas injetando as dependências necessárias.

        Args:
            repositorio_ferramentas: O repositório que provê acesso aos dados.
        """
        self._localizar_produto_service = LocalizarProdutoService(repositorio_ferramentas)
        self._localizar_talhao_service = LocalizarTalhaoService(repositorio_ferramentas)
        self._localizar_plantio_service = LocalizarPlantioService(repositorio_ferramentas)
        self._localizar_propriedade_service = LocalizarPropriedadeService(repositorio_ferramentas)
        self._localizar_maquina_service = LocalizarMaquinaService(repositorio_ferramentas)
        self._localizar_ponto_estoque_service = LocalizarPontoEstoqueService(repositorio_ferramentas)
        self._localizar_safra_service = LocalizarSafraService(repositorio_ferramentas)
        self._localizar_responsavel_service = LocalizarResponsavelService(repositorio_ferramentas)

    def buscar_produto_por_nome(self, base_url: str, id_produtor: str, nome_produto: str) -> Dict[str, Any]:
        """
        Busca produtos com base em um nome mencionado.

        Invoca o serviço de domínio para localizar produtos e retorna o resultado
        serializado.
        """
        resultado = self._localizar_produto_service.obterPossiveisProdutos(
            base_url=base_url,nome_produto_mencionado=nome_produto, id_produtor=id_produtor
        )
        return serializar_para_json(resultado)

    def buscar_talhoes_disponiveis(self, base_url: str, id_produtor: str) -> List[Dict[str, Any]]:
        """
        Busca todos os plantios através dos talhões disponíveis para o produtor.

        Invoca o serviço de domínio e retorna a lista de plantios serializada.
        """
        resultados = self._localizar_talhao_service.obter(base_url=base_url,id_produtor=id_produtor)
        return serializar_para_json(resultados)
    
    def buscar_plantios_disponiveis(self, base_url: str, id_produtor: str) -> List[Dict[str, Any]]:
        """
        Busca todos os plantios através disponíveis para o produtor.

        Invoca o serviço de domínio e retorna a lista de plantios serializada.
        """
        resultados = self._localizar_plantio_service.obter(base_url=base_url,id_produtor=id_produtor)
        return serializar_para_json(resultados)
    
    def buscar_propriedades_disponiveis(self, base_url: str, id_produtor: str) -> List[Dict[str, Any]]:
        """
        Busca todas as propriedades disponíveis para o produtor.

        Invoca o serviço de domínio e retorna a lista de propriedades serializada.
        """
        resultados = self._localizar_propriedade_service.obter(base_url=base_url,id_produtor=id_produtor)
        return serializar_para_json(resultados)

    def buscar_maquinas_disponiveis(self, base_url: str, id_produtor: str, nome_maquina: str) -> List[Dict[str, Any]]:
        """
        Busca máquinas com base em um termo de busca.

        Invoca o serviço de domínio para localizar máquinas e retorna o resultado
        serializado.
        """
        resultado = self._localizar_maquina_service.obter(
            base_url=base_url,id_produtor=id_produtor, termo_busca=nome_maquina
        )
        return serializar_para_json(resultado)

    def buscar_pontos_de_estoque_disponiveis(self, base_url: str, id_produtor: str, nome_ponto_estoque: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca pontos de estoque, opcionalmente filtrando por um nome.

        Invoca o serviço de domínio para localizar pontos de estoque e retorna o
        resultado serializado.
        """
        resultado = self._localizar_ponto_estoque_service.obter(
            base_url=base_url,id_produtor=id_produtor, nome_mencionado=nome_ponto_estoque
        )
        return serializar_para_json(resultado)
    
    def buscar_safra_disponivel(self, base_url: str, id_produtor: str, nome_safra: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Busca uma safra, opcionalmente filtrando por um nome.

        Invoca o serviço de domínio para localizar a safra e retorna o resultado
        serializado.
        """
        resultado = self._localizar_safra_service.obter(
            base_url=base_url,id_produtor=id_produtor, nome_mencionado=nome_safra
        )
        return json.dumps(resultado.model_dump() if resultado else None, default=json_converter)

    def buscar_responsavel_por_telefone(self, base_url: str, id_produtor: str, telefone: str) -> Optional[Dict[str, Any]]:
        """
        Busca um responsável pelo número de telefone.

        Invoca o serviço de domínio para localizar o responsável e retorna o
        resultado serializado.
        """
        resultado = self._localizar_responsavel_service.obter(
            base_url=base_url,telefone=telefone, id_produtor=id_produtor
        )
        return serializar_para_json(resultado)
    
def serializar_para_json(dados):
    if hasattr(dados, 'model_dump'): # Para objetos Pydantic
        return dados.model_dump(mode='json')
    if isinstance(dados, list): # Para listas de objetos
        return [serializar_para_json(item) for item in dados]
    if isinstance(dados, dict): # Para dicionários
        return {k: serializar_para_json(v) for k, v in dados.items()}
    if isinstance(dados, date):
        return dados.isoformat()
    return dados

def json_converter(o):
    if isinstance(o, date):
        return o.isoformat()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")