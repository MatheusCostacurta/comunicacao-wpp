from typing import List, Optional
from thefuzz import process
from src.comunicacao_wpp_ia.dominio.modelos.safra import Safra

class LocalizarSafraService:
    def __init__(self, api):
        self.api = api

    def obterSafra(self, id_produtor: int, nome_mencionado: Optional[str] = None) -> Optional[Safra]:
        """
        Encontra a safra. Se um nome for mencionado, busca por ele.
        Caso contrário, busca a safra ativa.
        """
        print(f"\n[SERVICE] Iniciando busca por Safra...")
        todas_safras = self.api.buscar_safras_do_produtor(id_produtor)

        if not todas_safras:
            return None

        # Se o usuário não especificou, retorna a safra ativa
        if not nome_mencionado:
            for safra in todas_safras:
                if safra.esta_ativa:
                    print("[SERVICE] Safra ativa encontrada.")
                    return safra
            return None # Nenhuma safra ativa encontrada

        # Se especificou, busca pelo nome
        nomes_safras = [s.nome for s in todas_safras]
        melhor_match, score = process.extractOne(nome_mencionado, nomes_safras)
        
        if score >= 80:
            print(f"[SERVICE] Safra encontrada por nome: {melhor_match} (Score: {score})")
            for safra in todas_safras:
                if safra.nome == melhor_match:
                    return safra
        
        print("[SERVICE] Nenhuma safra compatível encontrada.")
        return None