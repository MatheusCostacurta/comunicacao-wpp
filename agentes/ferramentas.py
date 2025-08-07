from typing import Dict, List, Optional
from langchain.tools import tool
from services.localizar_produto import product_finder_service 
from api.agriwin import api_mock

ID_PRODUTOR_EXEMPLO = 1 # ID fixo para este exemplo

@tool
def buscar_produto_por_nome(nome_produto: str) -> Optional[Dict]:
    """
    Use esta ferramenta para obter um map de produtos similares ao produto que usuário mencionou.
    Esse map é composto por 3 listas: produtos em estoque, produtos mais consumidos e produtos similares. 
    A IA deve então usar esse map para encontrar o ID do produto que o usuário mencionou, priorizando produtos que já foram consumidos ou que possuem estoque para casos de desempate.
    """
    return product_finder_service.find_product(nome_produto_mencionado=nome_produto, id_produtor=ID_PRODUTOR_EXEMPLO)

@tool
def buscar_talhoes_disponiveis() -> List[dict]:
    """Use esta ferramenta para obter uma lista de TODOS os talhões (áreas ou campos) disponíveis na fazenda do produtor. A IA deve então usar esta lista para encontrar o ID do talhão que o usuário mencionou."""
    return api_mock.get_talhoes_do_produtor(id_produtor=ID_PRODUTOR_EXEMPLO)

@tool
def buscar_maquinas_disponiveis() -> List[dict]:
    """Use esta ferramenta para obter uma lista de TODAS as máquinas (imobilizados) disponíveis para o produtor. A IA deve então usar esta lista para encontrar o ID da máquina que o usuário mencionou."""
    return api_mock.get_maquinas_do_produtor(id_produtor=ID_PRODUTOR_EXEMPLO)

# Lista de ferramentas para facilitar a importação
all_tools = [buscar_produto_por_nome, buscar_talhoes_disponiveis, buscar_maquinas_disponiveis]