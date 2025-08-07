from typing import List, Optional
from api.agriwin import api_mock
from thefuzz import process # Usaremos uma biblioteca para a busca de strings aproximada

class ProductFinderService:
    def __init__(self, api):
        self.api = api
        self.id_produtor = 1 # ID fixo para o exemplo

    def _buscar_candidatos(self, nome_produto: str, lista_produtos: List[dict], limite: Optional[int] = None) -> List[dict]:
        """Usa a biblioteca thefuzz para encontrar os melhores candidatos na lista."""
        nomes = [p["nome"] for p in lista_produtos]
        score = 80 # Definindo um score mínimo de 80 para considerar uma correspondência

        # Se limite não for informado, retorna todos acima do cutoff
        if limite is None:
            matches = process.extractBests(nome_produto, nomes, score_cutoff=score)
        else:
            matches = process.extractBests(nome_produto, nomes, score_cutoff=score, limit=limite)
        
        # Mapeia os nomes de volta para os objetos de produto completos
        candidatos = []
        for nome_match, score in matches:
            for produto in lista_produtos:
                if produto["nome"] == nome_match:
                    candidatos.append(produto)
                    break # para não adicionar o mesmo produto duas vezes
        return candidatos

    def find_product(self, nome_produto_mencionado: str, id_produtor: int) -> Optional[dict]:
        """
        Orquestra a busca pelo produto.
        """
        print(f"\n[SERVICE] Iniciando busca complexa para o produto: '{nome_produto_mencionado}'")
        produtos_similares = []
        produtos_em_estoque = []
        produtos_mais_usados = []

        # 1. Primeira chamada: Buscar produtos
        produtos_do_produtor = self.api.get_produtos_do_produtor(self.id_produtor)
        produtos_similares = self._buscar_candidatos(nome_produto_mencionado, produtos_do_produtor)

        if not produtos_similares:
            print("[SERVICE] Nenhum produto encontrado.")
            return None
        
        if len(produtos_similares) == 1:
            produto_encontrado = produtos_similares[0]
            print(f"[SERVICE] Sucesso! Encontrado 1 produto: {produto_encontrado['nome']}")
            return produto_encontrado
        
        # 2. Segunda chamada: Buscar produtos em estoque
        if len(produtos_similares) > 1:
            print(f"[SERVICE] Múltiplos produtos_similares encontrados: {[c['nome'] for c in produtos_similares]}. Verificando estoque e consumo...")
        
            produtos_em_estoque = self.api.get_produtos_em_estoque(self.id_produtor, produtos_similares)
            produtos_mais_usados = self.api.get_produtos_mais_consumidos(self.id_produtor, produtos_similares)

        return {
            "produtos_similares": produtos_similares,
            "produtos_em_estoque": produtos_em_estoque,
            "produtos_mais_usados": produtos_mais_usados
        }

# Instância do serviço para ser usada pelas ferramentas
product_finder_service = ProductFinderService(api=api_mock)