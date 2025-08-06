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
        Orquestra a busca pelo produto, aplicando a lógica de desempate se necessário.
        """
        print(f"\n[SERVICE] Iniciando busca complexa para o produto: '{nome_produto_mencionado}'")

        # 1. Primeira chamada: Buscar produtos
        produtos_do_produtor = self.api.get_produtos_do_produtor(self.id_produtor)
        candidatos = self._buscar_candidatos(nome_produto_mencionado, produtos_do_produtor)

        if not candidatos:
            print("[SERVICE] Nenhum produto encontrado.")
            return None
        
        if len(candidatos) == 1:
            produto_encontrado = candidatos[0]
            print(f"[SERVICE] Sucesso! Encontrado 1 produto: {produto_encontrado['nome']}")
            return produto_encontrado
        
        # 2. Segunda chamada: Buscar produtos em estoque
        if len(candidatos) > 1:
            #TODO: aqui preciso usar a IA para decidir, vou informar quais os produtos estao em estoque, quais foram os ultimos consumidos e deixar o poder de decisão pra ela.

            print(f"[SERVICE] Múltiplos candidatos encontrados: {[c['nome'] for c in candidatos]}. Verificando estoque...")
        
            produtos_em_estoque = self.api.get_produtos_em_estoque(self.id_produtor, candidatos)
            
            if len(produtos_em_estoque) == 1:
                produto_encontrado = produtos_em_estoque[0]
                print(f"[SERVICE] Sucesso! Encontrado 1 produto em estoque: {produto_encontrado['nome']}")
                return produto_encontrado

            # 3. Se encontrou mais de 1, usa a segunda API para desempate
            if len(produtos_em_estoque) > 1:
                print(f"[SERVICE] Múltiplos candidatos em estoque: {[c['nome'] for c in produtos_em_estoque]}. Usando critério de desempate...")
                
                produtos_mais_usados = self.api.get_produtos_mais_consumidos(self.id_produtor)
                
                # Compara os candidatos em estoque com a lista dos mais usados
                # Aquele que aparecer primeiro na lista de "mais usados" vence.
                for produto_mais_usado in produtos_mais_usados:
                    for candidato in produtos_em_estoque:
                        if candidato["id"] == produto_mais_usado["id"]:
                            print(f"[SERVICE] Desempate: '{candidato['nome']}' é o mais consumido recentemente.")
                            return candidato
                
                # Se nenhum dos candidatos estiver na lista de mais usados, retorna o primeiro por padrão
                print("[SERVICE] Nenhum dos candidatos está na lista de mais consumidos. Retornando o primeiro.")
                return produtos_em_estoque[0]
            
            # Se nenhum dos produtos possuem estoque, retorna o primeiro candidato original
            print("[SERVICE] Nenhum dos candidatos está em estoque. Retornando o primeiro.")
            return candidatos[0]

# Instância do serviço para ser usada pelas ferramentas
product_finder_service = ProductFinderService(api=api_mock)