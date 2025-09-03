import json
from datetime import date
from typing import Optional, List
from langchain.tools import tool

from src.comunicacao_wpp_ia.dominio.servicos.localizar_produto import LocalizarProdutoService 
from src.comunicacao_wpp_ia.dominio.servicos.localizar_ponto_estoque import LocalizarPontoEstoqueService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_safra import LocalizarSafraService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_talhao import LocalizarTalhaoService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_propriedade import LocalizarPropriedadeService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_maquina import LocalizarMaquinaService
from src.comunicacao_wpp_ia.dominio.servicos.localizar_responsavel import LocalizarResponsavelService


from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.repositorios.agriwin_ferramentas import RepoAgriwinFerramentas
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.repositorios.agriwin_consumo import RepoAgriwinConsumo

from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.clientes_api.agriwin_cliente import AgriwinCliente

ID_PRODUTOR_EXEMPLO = 57 # ID fixo para este exemplo
agriwin_urls = ["https://demo.agriwin.com.br"]
agriwin_cliente = AgriwinCliente(base_urls=agriwin_urls)
api_agriwin_ferramentas = RepoAgriwinFerramentas(agriwin_cliente=agriwin_cliente)
api_agriwin_consumo = RepoAgriwinConsumo(agriwin_cliente=agriwin_cliente)

class LangChainFerramentas:
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
    Use esta ferramenta para obter um map de produtos similares com base no produto que usuário mencionou.
    A menção do usuário pode ser o nome do produto (ex: 'Tordon') ou um ingrediente ativo (ex: 'Glifosato').
    Esse map é composto por 3 listas: 'produtos_similares', 'produtos_em_estoque' e 'produtos_mais_consumidos'.
    Cada produto no retorno conterá seu ID, nome, descrição, e também uma lista de 'unidades_medida' e 'ingredientes_ativos'.
    A IA deve usar esse map para encontrar o ID do produto que o usuário mencionou, priorizando produtos que já foram consumidos ou que possuem estoque para casos de desempate.
    Retorna um JSON string com listas de produtos similares, em estoque e mais consumidos.
    """
    if not nome_produto or not isinstance(nome_produto, str):
        print("[FERRAMENTA BLINDADA] 'buscar_produto_por_nome' recebeu um nome de produto inválido. Retornando vazio.")
        return json.dumps({"produtos_similares": [], "produtos_em_estoque": [], "produtos_mais_usados": []})
   
    produto_service = LocalizarProdutoService(api_ferramentas = api_agriwin_ferramentas)
    resultado = produto_service.obterPossiveisProdutos(nome_produto_mencionado=nome_produto, id_produtor=ID_PRODUTOR_EXEMPLO)
    return json.dumps(serializar_para_json(resultado))

@tool
def buscar_talhoes_disponiveis() -> str:
    """Use esta ferramenta para obter uma lista de TODOS os talhões (áreas ou campos) disponíveis na fazenda do produtor. A IA deve então usar esta lista para encontrar o ID do talhão que o usuário mencionou.
    Retorna um JSON string com a lista de TODOS os talhões disponíveis."""
    talhao_service = LocalizarTalhaoService(api_ferramentas=api_agriwin_ferramentas)
    resultados = talhao_service.obter(id_produtor=ID_PRODUTOR_EXEMPLO)
    return json.dumps(serializar_para_json(resultados))

@tool
def buscar_propriedades_disponiveis() -> str:
    """Use esta ferramenta para obter uma lista de TODAS as propriedades (fazendas) disponíveis para o produtor. A IA deve usar esta lista para encontrar o(s) ID(s) da(s) propriedade(s) que o usuário mencionou.
    Retorna um JSON string com a lista de TODAS as propriedades disponíveis."""
    propriedade_service = LocalizarPropriedadeService(api_ferramentas=api_agriwin_ferramentas)
    resultados = propriedade_service.obter(id_produtor=ID_PRODUTOR_EXEMPLO)
    return json.dumps(serializar_para_json(resultados))

@tool
def buscar_maquinas_disponiveis(nome_maquina: str) -> str:
    """
    Use esta ferramenta para encontrar uma ou mais máquinas (imobilizados) com base no que o usuário mencionou.
    O termo de busca pode ser o nome da máquina (ex: 'Trator John Deere') ou o seu número de série (ex: 'JD6110JBR').
    A ferramenta buscará por similaridade no nome (score 80) ou por correspondência exata no número de série.
    A IA deve então usar esta lista para encontrar o ID da máquina que o usuário mencionou

    Retorna um JSON string com a lista de máquinas encontradas.
    """
    if not nome_maquina or not isinstance(nome_maquina, str):
        print("[FERRAMENTA BLINDADA] 'buscar_maquinas_disponiveis' recebeu um nome de máquina inválido. Retornando vazio.")
        return json.dumps([])
    maquina_service = LocalizarMaquinaService(api_ferramentas=api_agriwin_ferramentas)
    resultado = maquina_service.obter(id_produtor=ID_PRODUTOR_EXEMPLO, termo_busca=nome_maquina)
    return json.dumps(serializar_para_json(resultado))

@tool
def buscar_pontos_de_estoque_disponiveis(nome_ponto_estoque: Optional[str] = None) -> str:
    """
    Use esta ferramenta para encontrar o ID do ponto de estoque (depósito) que o usuário mencionou. Forneça o nome mencionado para encontrar o melhor candidato.
    - Se o usuário mencionou um nome (ex: 'depósito da sede'), passe a string para o parâmetro 'nome_ponto_estoque'. A ferramenta retornará uma lista de pontos de estoque com nome similar ou vazia.
    - Se o usuário NÃO mencionou um ponto de estoque, chame a ferramenta sem nenhum parâmetro (deixe como None).
    """
    service = LocalizarPontoEstoqueService(api_ferramentas = api_agriwin_ferramentas)
    resultado = service.obter(id_produtor=ID_PRODUTOR_EXEMPLO,nome_mencionado=nome_ponto_estoque)
    return json.dumps(serializar_para_json(resultado))

@tool
def buscar_safra_disponivel(nome_safra: Optional[str] = None) -> str:
    """
    Use esta ferramenta para encontrar a safra. 
    - Se o usuário mencionou um período (ex: 'safra 24/25', '2023/2024'), passe a string para o parâmetro 'nome_safra'.
    - Se o usuário NÃO mencionou um período de safra, chame a ferramenta sem nenhum parâmetro para obter a safra atual com base na data de hoje.

    Retorna um JSON string com a safra encontrada (pelo nome ou a safra ativa).
    """
    service = LocalizarSafraService(api_ferramentas = api_agriwin_ferramentas)
    resultado = service.obter(id_produtor=ID_PRODUTOR_EXEMPLO, nome_mencionado=nome_safra)
    return json.dumps(resultado.model_dump() if resultado else None, default=json_converter)

@tool
def buscar_responsavel_por_telefone(telefone: str) -> str:
    """Use esta ferramenta para encontrar o ID do responsável com base no número de telefone do remetente.
    Retorna um JSON string com o responsável encontrado pelo telefone."""

    if not telefone or not isinstance(telefone, str):
        print("[FERRAMENTA BLINDADA] 'buscar_responsavel_por_telefone' recebeu um telefone inválido. Retornando nulo.")
        return json.dumps(None)
    
    responsavel_service = LocalizarResponsavelService(api_ferramentas=api_agriwin_ferramentas)
    resultado = responsavel_service.obter(telefone=telefone, id_produtor=ID_PRODUTOR_EXEMPLO)
    return json.dumps(resultado.dict() if resultado else None)

@tool
def salvar_registro_consumo(
    id_produto: int, 
    quantidade: str, 
    id_ponto_estoque: int, 
    id_safra: int, 
    data_aplicacao: str, 
    tipo_rateio: str, 
    ids_talhoes: Optional[List[int]] = None, 
    ids_propriedades: Optional[List[int]] = None, 
    id_responsavel: Optional[int] = None, 
    id_maquina: Optional[int] = None,
    horimetro_inicio: Optional[float] = None,
    horimetro_fim: Optional[float] = None
) -> str:   
    """
    Use esta ferramenta como a ETAPA FINAL para salvar o registro de consumo.
    A data deve estar no formato 'YYYY-MM-DD'.
    Se uma máquina foi usada, inclua os parâmetros 'id_maquina', 'horimetro_inicio' e 'horimetro_fim'.
    Se o tipo_rateio for 'talhao', você DEVE fornecer uma lista de IDs em 'ids_talhoes'.
    Se o tipo_rateio for 'propriedade', você DEVE fornecer uma lista de IDs em 'ids_propriedades'.
    Esta ferramenta fará o POST para a API e retorna um JSON string com o 'status_code' e a 'mensagem' da API.
    """
    
    print("Iniciou ferramenta salvar_registro_consumo")
    
    campos_obrigatorios = {
        "id_produto": id_produto,
        "quantidade": quantidade,
        "id_ponto_estoque": id_ponto_estoque,
        "id_safra": id_safra,
        "data_aplicacao": data_aplicacao,
        "tipo_rateio": tipo_rateio,
    }
    campos_faltantes = [nome for nome, valor in campos_obrigatorios.items() if valor is None]
    if campos_faltantes:
        msg_erro = f"Parâmetros obrigatórios ausentes para salvar o consumo: {', '.join(campos_faltantes)}."
        print(f"[FERRAMENTA BLINDADA] {msg_erro}")
        return json.dumps({"status_code": 400, "message": msg_erro})
    
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
        dados_para_salvar["horimetro_inicio"] = horimetro_inicio
        dados_para_salvar["horimetro_fim"] = horimetro_fim

    print("Dados preparados para salvar consumo:", dados_para_salvar)
    status_code, response_body = api_agriwin_consumo.salvar_consumo(dados_consumo=dados_para_salvar)
    
    resultado_final = {
        "status_code": status_code,
        "message": response_body.get("message", "Ocorreu um erro desconhecido.")
    }

    return json.dumps(resultado_final)


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

# TODO: MELHORAR
def json_converter(o):
    if isinstance(o, date):
        return o.isoformat()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")