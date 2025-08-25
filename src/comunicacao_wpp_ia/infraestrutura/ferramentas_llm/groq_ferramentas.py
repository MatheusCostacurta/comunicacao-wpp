import json
from typing import Optional, List
from langchain.tools import tool
from src.comunicacao_wpp_ia.dominio.servicos.localizar_produto import LocalizarProdutoService 
from src.comunicacao_wpp_ia.dominio.servicos.localizar_ponto_estoque import LocalizarPontoEstoqueService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_safra import LocalizarSafraService
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.repositorios.agriwin_ferramentas import RepoAgriwinFerramentas
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.repositorios.agriwin_consumo import RepoAgriwinConsumo

ID_PRODUTOR_EXEMPLO = 1 # ID fixo para este exemplo
api_agriwin_ferramentas = RepoAgriwinFerramentas()
api_agriwin_consumo = RepoAgriwinConsumo()

class GroqFerramentas:
    """
    Define as ferramentas que a IA pode usar para interagir com o sistema.
    """
    pass

    def __init__(self):
        self.todas_ferramentas = [
            buscar_produto_por_nome, 
            buscar_talhoes_disponiveis, 
            buscar_propriedades_disponiveis,
            buscar_maquinas_disponiveis, 
            buscar_pontos_de_estoque_disponiveis,
            buscar_safra_disponivel,             
            buscar_responsavel_por_telefone,     
            salvar_registro_consumo
        ]

    def obter(self):
        return self.todas_ferramentas
    
@tool
def buscar_produto_por_nome(nome_produto: str) -> str:
    """
    Use esta ferramenta para obter um map de produtos similares ao produto que usuário mencionou.
    Esse map é composto por 3 listas: produtos em estoque, produtos mais consumidos e produtos similares. 
    A IA deve então usar esse map para encontrar o ID do produto que o usuário mencionou, priorizando produtos que já foram consumidos ou que possuem estoque para casos de desempate.
    Retorna um JSON string com listas de produtos similares, em estoque e mais consumidos.
    """
    produto_service = LocalizarProdutoService(api_ferramentas = api_agriwin_ferramentas)
    resultado = produto_service.obterPossiveisProdutos(nome_produto_mencionado=nome_produto, id_produtor=ID_PRODUTOR_EXEMPLO)
    resultado_serializado = serializar_para_json(resultado)
    return json.dumps(resultado_serializado)

@tool
def buscar_talhoes_disponiveis() -> str:
    """Use esta ferramenta para obter uma lista de TODOS os talhões (áreas ou campos) disponíveis na fazenda do produtor. A IA deve então usar esta lista para encontrar o ID do talhão que o usuário mencionou.
    Retorna um JSON string com a lista de TODOS os talhões disponíveis."""
    resultados = api_agriwin_ferramentas.buscar_talhoes_do_produtor(id_produtor=ID_PRODUTOR_EXEMPLO)
    return json.dumps(serializar_para_json(resultados))

@tool
def buscar_propriedades_disponiveis() -> str:
    """Use esta ferramenta para obter uma lista de TODAS as propriedades (fazendas) disponíveis para o produtor. A IA deve usar esta lista para encontrar o(s) ID(s) da(s) propriedade(s) que o usuário mencionou.
    Retorna um JSON string com a lista de TODAS as propriedades disponíveis."""
    resultados = api_agriwin_ferramentas.buscar_propriedades_do_produtor(id_produtor=ID_PRODUTOR_EXEMPLO)
    return json.dumps(serializar_para_json(resultados))

@tool
def buscar_maquinas_disponiveis() -> str:
    """Use esta ferramenta para obter uma lista de TODAS as máquinas (imobilizados) disponíveis para o produtor. A IA deve então usar esta lista para encontrar o ID da máquina que o usuário mencionou.
    Retorna um JSON string com a lista de TODAS as máquinas disponíveis."""
    resultados = api_agriwin_ferramentas.buscar_maquinas_do_produtor(id_produtor=ID_PRODUTOR_EXEMPLO)
    return json.dumps(serializar_para_json(resultados))

@tool
def buscar_pontos_de_estoque_disponiveis(nome_ponto_estoque: str) -> str:
    """Use esta ferramenta para encontrar o ID do ponto de estoque (depósito) que o usuário mencionou. Forneça o nome mencionado para encontrar o melhor candidato.
    Retorna um JSON string com o melhor candidato para o ponto de estoque mencionado."""
    service = LocalizarPontoEstoqueService(api_ferramentas = api_agriwin_ferramentas)
    resultado = service.obterMelhorCandidato(nome_mencionado=nome_ponto_estoque, id_produtor=ID_PRODUTOR_EXEMPLO)
    return json.dumps(resultado.dict() if resultado else None)

@tool
def buscar_safra_disponivel(nome_safra: Optional[str] = None) -> str:
    """
    Use esta ferramenta para encontrar a safra. 
    - Se o usuário mencionou um nome de safra (ex: 'safra de soja'), passe o nome para o parâmetro 'nome_safra'.
    - Se o usuário NÃO mencionou uma safra, chame a ferramenta sem parâmetros para obter a safra atual/ativa.

    Retorna um JSON string com a safra encontrada (pelo nome ou a safra ativa).
    """
    service = LocalizarSafraService(api_ferramentas = api_agriwin_ferramentas)
    resultado = service.obterSafra(id_produtor=ID_PRODUTOR_EXEMPLO, nome_mencionado=nome_safra)
    return json.dumps(resultado.dict() if resultado else None)

@tool
def buscar_responsavel_por_telefone(telefone: str) -> str:
    """Use esta ferramenta para encontrar o ID do responsável com base no número de telefone do remetente.
    Retorna um JSON string com o responsável encontrado pelo telefone."""
    resultado = api_agriwin_ferramentas.buscar_responsavel_por_telefone(id_produtor=ID_PRODUTOR_EXEMPLO, telefone=telefone)
    return json.dumps(resultado.dict() if resultado else None)

@tool
def salvar_registro_consumo(id_produto: int, quantidade: str, id_ponto_estoque: int, id_safra: int, data_aplicacao: str, tipo_rateio: str, ids_talhoes: Optional[List[int]] = None, ids_propriedades: Optional[List[int]] = None, id_responsavel: Optional[int] = None, id_maquina: Optional[int] = None) -> str:
    """
    Use esta ferramenta como a ETAPA FINAL para salvar o registro de consumo.
    A data deve estar no formato 'YYYY-MM-DD'.
    Se o tipo_rateio for 'talhao', você DEVE fornecer uma lista de IDs em 'ids_talhoes'.
    Se o tipo_rateio for 'propriedade', você DEVE fornecer uma lista de IDs em 'ids_propriedades'.
    Esta ferramenta fará o POST para a API e retorna um JSON string com o 'status_code' e a 'mensagem' da API.
    """
    dados_para_salvar = {
        "id_produto": id_produto,
        "quantidade": quantidade,
        "id_ponto_estoque": id_ponto_estoque,
        "id_safra": id_safra,
        "data_aplicacao": data_aplicacao,
        "tipo_rateio": tipo_rateio,
    }
    
    if ids_talhoes:
        dados_para_salvar["ids_talhoes"] = ids_talhoes
    if ids_propriedades:
        dados_para_salvar["ids_propriedades"] = ids_propriedades
    if id_responsavel:
        dados_para_salvar["id_responsavel"] = id_responsavel
    if id_maquina:
        dados_para_salvar["id_maquina"] = id_maquina

    status_code, response_body = api_agriwin_consumo.salvar_consumo(dados_consumo=dados_para_salvar)
    
    resultado_final = {
        "status_code": status_code,
        "message": response_body.get("message", "Ocorreu um erro desconhecido.")
    }

    return json.dumps(resultado_final)


def serializar_para_json(dados):
    if hasattr(dados, 'model_dump'): # Para objetos Pydantic
        return dados.model_dump()
    if isinstance(dados, list): # Para listas de objetos
        return [serializar_para_json(item) for item in dados]
    if isinstance(dados, dict): # Para dicionários
        return {k: serializar_para_json(v) for k, v in dados.items()}
    return dados