from typing import Dict, List, Optional
from langchain.tools import tool
from comunicacao_wpp_ia.dominio.servicos.localizar_produto import LocalizarProdutoService 
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.clientes_api.agriwin_rotas import RotasAgriwin

ID_PRODUTOR_EXEMPLO = 1 # ID fixo para este exemplo
api_agriwin = RotasAgriwin()

class GroqFerramentas:
    """
    Define as ferramentas que a IA pode usar para interagir com o sistema.
    """
    pass

    def __init__(self):
        self.todas_ferramentas = [
            buscar_produto_por_nome, 
            buscar_talhoes_disponiveis, 
            buscar_maquinas_disponiveis, 
            salvar_registro_consumo
        ]

    def obter(self):
        return self.todas_ferramentas
    
@tool
def buscar_produto_por_nome(nome_produto: str) -> Optional[Dict]:
    """
    Use esta ferramenta para obter um map de produtos similares ao produto que usuário mencionou.
    Esse map é composto por 3 listas: produtos em estoque, produtos mais consumidos e produtos similares. 
    A IA deve então usar esse map para encontrar o ID do produto que o usuário mencionou, priorizando produtos que já foram consumidos ou que possuem estoque para casos de desempate.
    """
    produto_service = LocalizarProdutoService(api=RotasAgriwin())
    return produto_service.obterPossiveisProdutos(nome_produto_mencionado=nome_produto, id_produtor=ID_PRODUTOR_EXEMPLO)

@tool
def buscar_talhoes_disponiveis() -> List[dict]:
    """Use esta ferramenta para obter uma lista de TODOS os talhões (áreas ou campos) disponíveis na fazenda do produtor. A IA deve então usar esta lista para encontrar o ID do talhão que o usuário mencionou."""
    return api_agriwin.buscar_talhoes_do_produtor(id_produtor=ID_PRODUTOR_EXEMPLO)

@tool
def buscar_maquinas_disponiveis() -> List[dict]:
    """Use esta ferramenta para obter uma lista de TODAS as máquinas (imobilizados) disponíveis para o produtor. A IA deve então usar esta lista para encontrar o ID da máquina que o usuário mencionou."""
    return api_agriwin.buscar_maquinas_do_produtor(id_produtor=ID_PRODUTOR_EXEMPLO)

@tool
def salvar_registro_consumo(id_produto: int, quantidade: str, id_talhao: int, id_maquina: Optional[int] = None) -> Dict:
    """
    Use esta ferramenta como a ETAPA FINAL para salvar o registro de consumo.
    Esta ferramenta fará o POST para a API e retorna um dicionário com o 'status_code' e a 'mensagem' da API.
    """
    dados_para_salvar = {
        "id_produto": id_produto,
        "quantidade": quantidade,
        "id_talhao": id_talhao,
    }
    if id_maquina:
        dados_para_salvar["id_maquina"] = id_maquina

    status_code, response_body = api_agriwin.salvar_consumo(dados_consumo=dados_para_salvar)
    
    return {
        "status_code": status_code,
        "message": response_body.get("message", "Ocorreu um erro desconhecido.")
    }
