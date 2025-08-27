from typing import Dict, Tuple
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_consumo import RepositorioConsumo


class RepoAgriwinConsumo(RepositorioConsumo):
    """
    Adaptador que implementa as interfaces de repositório para o remetente.
    """
    def __init__(self):
        print("[INFRA] Adaptador do Repositório AgriwinRemetente inicializado.")
    

    def salvar_consumo(self, dados_consumo: Dict) -> Tuple[int, Dict]:
        """
        Simula o POST para salvar os dados de consumo na API interna.
        Retorna uma tupla contendo o status_code e o corpo da resposta em JSON.
        """
        print(f"\n[API MOCK] Recebido POST para salvar consumo: {dados_consumo}")
        
        # Simulação de erro de validação da API (Internal Server Error)
        if dados_consumo.get("quantidade") == "20 kg" and dados_consumo.get("id_produto") == 102:
            response_body = {
                "error": "VALIDATION_ERROR",
                "message": "Erro de validação: A quantidade '20 kg' para 'Adubo Super Simples' excede o limite permitido por aplicação."
            }
            return 500, response_body
        
        # Simulação de sucesso (OK)
        id_locais = dados_consumo.get('ids_talhoes') or dados_consumo.get('ids_propriedades', [])
        local_str = "talhão(ões) ID(s)" if 'ids_talhoes' in dados_consumo else "propriedade(s) ID(s)"

        response_body = {
            "status": "sucesso",
            "message": f"Consumo do produto ID {dados_consumo.get('id_produto')} registrado com sucesso no(a) {local_str} {id_locais}.",
            "registro_id": 12345 
        }
        return 200, response_body
