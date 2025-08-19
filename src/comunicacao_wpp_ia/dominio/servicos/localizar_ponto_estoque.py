from typing import List, Optional
from thefuzz import process
from src.comunicacao_wpp_ia.dominio.modelos.ponto_estoque import PontoEstoque

class LocalizarPontoEstoqueService:
    def __init__(self, api):
        self.api = api

    def obterMelhorCandidato(self, nome_mencionado: str, id_produtor: int) -> Optional[PontoEstoque]:
        """Encontra o ponto de estoque mais provável com base no nome."""
        print(f"\n[SERVICE] Iniciando busca por Ponto de Estoque: '{nome_mencionado}'")
        todos_pontos_estoque = self.api.buscar_pontos_estoque_do_produtor(id_produtor)
        
        if not todos_pontos_estoque:
            return None

        nomes_pontos_estoque = [p.nome for p in todos_pontos_estoque]
        
        # Usamos extractOne para pegar o melhor resultado acima de um score
        melhor_match, score = process.extractOne(nome_mencionado, nomes_pontos_estoque)
        
        if score >= 80:
            print(f"[SERVICE] Ponto de estoque encontrado: {melhor_match} (Score: {score})")
            for ponto in todos_pontos_estoque:
                if ponto.nome == melhor_match:
                    return ponto
        
        print("[SERVICE] Nenhum ponto de estoque compatível encontrado.")
        return None