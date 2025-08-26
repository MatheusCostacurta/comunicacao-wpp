import re
from typing import List, Optional
from datetime import date
from src.comunicacao_wpp_ia.dominio.modelos.safra import Safra

class LocalizarSafraService:
    def __init__(self, api_ferramentas):
        self.api = api_ferramentas

    def _extrair_anos(self, texto: str) -> Optional[tuple[int, int]]:
        """Extrai um padrão de ano como '24/25' ou '2024/2025' do texto."""
        # Procura por padrões como 24/25, 2024/2025, 2024 / 25, etc.
        match = re.search(r'(\d{2,4})\s*/\s*(\d{2,4})', texto)
        if not match:
            return None

        ano1_str, ano2_str = match.groups()
        
        # Converte anos de 2 dígitos para 4 dígitos
        ano1 = int(ano1_str) + 2000 if len(ano1_str) == 2 else int(ano1_str)
        ano2 = int(ano2_str) + 2000 if len(ano2_str) == 2 else int(ano2_str)

        return sorted((ano1, ano2))
    
    def obter(self, id_produtor: int, nome_mencionado: Optional[str] = None) -> Optional[Safra]:
        """
        Encontra a safra. Se um nome for mencionado, busca por ele.
        Caso contrário, busca a safra que corresponde à data atual.
        """
        print(f"\n[SERVICE] Iniciando busca por Safra...")
        todas_safras = self.api.buscar_safras_do_produtor(id_produtor)

        if not todas_safras:
            return None

        # Se o usuário NÃO mencionou um nome, busca pela data atual
        if not nome_mencionado:
            hoje = date.today()
            print(f"[SERVICE] Buscando safra atual para a data: {hoje}")
            for safra in todas_safras:
                if safra.data_inicio <= hoje <= safra.data_termino:
                    print(f"[SERVICE] Safra atual encontrada: {safra.nome}")
                    return safra
            print("[SERVICE] Nenhuma safra ativa encontrada para a data atual.")
            return None

        # Se o usuário mencionou um nome, tenta extrair os anos
        anos_extraidos = self._extrair_anos(nome_mencionado)
        if not anos_extraidos:
            print(f"[SERVICE] Não foi possível extrair um padrão de ano de '{nome_mencionado}'.")
            return None
        
        ano_inicio_mencionado, ano_termino_mencionado = anos_extraidos
        print(f"[SERVICE] Buscando safra para o período: {ano_inicio_mencionado}/{ano_termino_mencionado}")

        for safra in todas_safras:
            if safra.ano_inicio == ano_inicio_mencionado and safra.ano_termino == ano_termino_mencionado:
                print(f"[SERVICE] Safra encontrada por ano: {safra.nome}")
                return safra
        
        print(f"[SERVICE] Nenhuma safra encontrada para o período {ano_inicio_mencionado}/{ano_termino_mencionado}.")
        return None