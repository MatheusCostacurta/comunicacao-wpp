from typing import List
from thefuzz import process
from src.comunicacao_wpp_ia.dominio.modelos.imobilizado import Imobilizado

class LocalizarMaquinaService:
    def __init__(self, api_ferramentas):
        self.api = api_ferramentas

    def obter(self, id_produtor: int, termo_busca: str) -> List[Imobilizado]:
        """
        Encontra máquinas com base em um termo de busca.
        - Se o termo for um número de série, busca por correspondência exata.
        - Se for um nome, busca por similaridade (score >= 80).
        """
        print(f"\n[SERVICE] Iniciando busca por Máquina: '{termo_busca}'")
        todas_maquinas = self.api.buscar_maquinas_do_produtor(id_produtor)

        if not todas_maquinas:
            return []

        # Etapa 1: Busca por correspondência exata no número de série
        termo_busca_lower = termo_busca.lower()
        for maquina in todas_maquinas:
            if maquina.numero_serie and maquina.numero_serie.lower() == termo_busca_lower:
                print(f"[SERVICE] Máquina encontrada por número de série exato: {maquina.nome}")
                return [maquina]
        
        # Etapa 2: Se não encontrou por S/N, busca por similaridade no nome
        print("[SERVICE] Nenhum S/N correspondente. Buscando por similaridade no nome...")
        nomes_maquinas = {m.id: m.nome for m in todas_maquinas}
        score_minimo = 80
        
        matches = process.extractBests(termo_busca, [m.nome for m in todas_maquinas], score_cutoff=score_minimo)
        
        if not matches:
            print("[SERVICE] Nenhuma máquina compatível encontrada.")
            return []

        maquinas_encontradas = []
        nomes_encontrados = [match[0] for match in matches]
        
        print(f"[SERVICE] Máquinas encontradas com similaridade: {nomes_encontrados}")
        for maquina in todas_maquinas:
            if maquina.nome in nomes_encontrados:
                maquinas_encontradas.append(maquina)
        
        return maquinas_encontradas