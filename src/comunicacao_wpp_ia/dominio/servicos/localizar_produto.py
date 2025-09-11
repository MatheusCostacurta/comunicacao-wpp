from typing import List, Optional, Dict, Any
from thefuzz import fuzz
from src.comunicacao_wpp_ia.dominio.modelos.produto import Produto

class LocalizarProdutoService:
    def __init__(self, api_ferramentas):
        self.api = api_ferramentas

    def __obter_candidatos(self, nome_mencionado: str, lista_produtos: List[dict], limite: Optional[int] = None) -> List[dict]:
        """
        Encontra produtos candidatos com base na similaridade do nome (score >= 80) 
        OU dos ingredientes ativos (score >= 90).
        """
        candidatos_encontrados = {}  # Usar um dicionário para evitar duplicatas, com ID como chave
        nome_mencionado_lower = nome_mencionado.lower()
        score_nome_minimo = 80
        score_ingrediente_minimo = 90

        for produto in lista_produtos:
            # 1. Compara com o nome do produto
            score_nome = fuzz.ratio(nome_mencionado_lower, produto.nome.lower())
            if score_nome >= score_nome_minimo:
                candidatos_encontrados[produto.id] = produto
                continue  # Pula para o próximo produto, pois a condição já foi atendida

            # 2. Se não encontrou pelo nome, compara com os ingredientes ativos
            if produto.ingredientes_ativos:
                for ingrediente in produto.ingredientes_ativos:
                    score_ingrediente = fuzz.ratio(nome_mencionado_lower, ingrediente.lower())
                    if score_ingrediente >= score_ingrediente_minimo:
                        candidatos_encontrados[produto.id] = produto
                        break  # Sai do loop de ingredientes, pois já adicionou o produto
        
        return list(candidatos_encontrados.values())

    def obterPossiveisProdutos(self, base_url: str, nome_produto_mencionado: str, id_produtor: int) -> Dict[str, Any]:
        """
        Orquestra a busca pelo produto e SEMPRE retorna um dicionário.
        """
        print(f"\n[SERVICE] Iniciando busca complexa para o produto: '{nome_produto_mencionado}'")
        produtos_similares = []
        produtos_em_estoque = []
        produtos_mais_usados = []

        # 1. Primeira chamada: Buscar produtos
        produtos_do_produtor = self.api.buscar_produtos_do_produtor(base_url, id_produtor)
        produtos_similares = self.__obter_candidatos(nome_produto_mencionado, produtos_do_produtor)

        if not produtos_similares:
            print("[SERVICE] Nenhum produto encontrado.")
            return {
                "produtos_similares": [],
                "produtos_em_estoque": [],
                "produtos_mais_usados": []
            }
        
        if len(produtos_similares) == 1:
            produto_encontrado = produtos_similares[0]
            print(f"[SERVICE] Sucesso! Encontrado 1 produto: {produto_encontrado.nome}")
            return {
                "produtos_similares": produtos_similares,
                "produtos_em_estoque": [],
                "produtos_mais_usados": []
            }
        
        # 2. Segunda chamada: Buscar produtos em estoque
        if len(produtos_similares) > 1:
            nomes_similares = [c.nome for c in produtos_similares]
            print(f"[SERVICE] Múltiplos produtos_similares encontrados: {nomes_similares}. Verificando estoque e consumo...")
            
            # produtos_em_estoque = self.api.buscar_produtos_em_estoque(base_url, id_produtor, produtos_similares)
            # produtos_mais_usados = self.api.buscar_produtos_mais_consumidos(base_url, id_produtor, produtos_similares)

        return {
            "produtos_similares": produtos_similares,
            "produtos_em_estoque": produtos_em_estoque,
            "produtos_mais_usados": produtos_mais_usados
        }
