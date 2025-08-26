from typing import Optional, List
from thefuzz import process
from src.comunicacao_wpp_ia.dominio.modelos.ponto_estoque import PontoEstoque

class LocalizarPontoEstoqueService:
    def __init__(self, api_ferramentas):
        self.api = api_ferramentas

    def obter(self, id_produtor: int, nome_mencionado: Optional[str] = None) -> List[PontoEstoque]:
        """
        Encontra pontos de estoque com base em um nome mencionado ou retorna o padrão se for o único disponível.
        - Se houver apenas um ponto de estoque, retorna-o como padrão.
        - Se um nome for mencionado, retorna todos os pontos com similaridade >= 80.
        - Se nenhum nome for mencionado e houver múltiplos pontos, retorna uma lista vazia.
        """
        print(f"\n[SERVICE] Iniciando busca por Ponto de Estoque: '{nome_mencionado or 'Nenhum'}'")
        todos_pontos_estoque = self.api.buscar_pontos_estoque_do_produtor(id_produtor)
        
        if not todos_pontos_estoque:
            return []

        # Se houver apenas um ponto de estoque, ele é o padrão.
        if len(todos_pontos_estoque) == 1:
            print(f"[SERVICE] Encontrado um único ponto de estoque como padrão: {todos_pontos_estoque[0].nome}")
            return todos_pontos_estoque

        # Se o usuário não mencionou um nome e há múltiplos, não há o que fazer.
        if not nome_mencionado:
            print("[SERVICE] Nenhum nome de ponto de estoque foi mencionado e existem múltiplos disponíveis.")
            return []

        # Se mencionou, busca por similaridade
        nomes_pontos_estoque = [p.nome for p in todos_pontos_estoque]
        score_minimo = 80
        
        # Usamos extractBests para pegar todos os resultados acima de um score
        matches = process.extractBests(nome_mencionado, nomes_pontos_estoque, score_cutoff=score_minimo)
        
        if not matches:
            print("[SERVICE] Nenhum ponto de estoque compatível encontrado.")
            return []

        pontos_encontrados = []
        nomes_encontrados = [match[0] for match in matches]
        
        print(f"[SERVICE] Pontos de estoque encontrados com similaridade: {nomes_encontrados}")
        for ponto in todos_pontos_estoque:
            if ponto.nome in nomes_encontrados:
                pontos_encontrados.append(ponto)
        
        return pontos_encontrados