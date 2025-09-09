import json
from typing import Dict, Tuple
from requests import HTTPError
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_consumo import RepositorioConsumo
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.clientes_api.agriwin_cliente import AgriwinCliente


class RepoAgriwinConsumo(RepositorioConsumo):
    """
    Adaptador que implementa as interfaces de repositório para o remetente.
    """
    def __init__(self, agriwin_cliente: AgriwinCliente):
        self._cliente = agriwin_cliente
        print("[INFRA] Adaptador do Repositório AgriwinRemetente inicializado.")
    

    def salvar(self, produtor_id: int, dados_consumo: Dict) -> Tuple[int, Dict]:
        """
        Envia os dados de consumo para a API Agriwin através de um POST.
        Retorna uma tupla contendo o status_code e o corpo da resposta em JSON.
        """
        endpoint = "/api/v1/consumos"
        payload_completo = {
            "identificador_produtor": produtor_id,
            "consumo": dados_consumo
        }
        print(f"\n[API] Enviando POST para salvar consumo em {endpoint}: {json.dumps(payload_completo, indent=4)}")

        try:
            response = self._cliente.post(endpoint, data=payload_completo)
            
            # A resposta de sucesso (2xx) já é tratada no AgriwinCliente.
            # Se chegamos aqui, a requisição foi bem-sucedida.
            response_body = response.json()
            return response.status_code, response_body

        except HTTPError as e:
            # O AgriwinCliente lança HTTPError para respostas 4xx e 5xx.
            # Podemos capturar o erro para extrair o corpo da resposta de erro da API.
            print(f"[API ERROR] Erro ao salvar consumo: {e.response.status_code} - {e.response.text}")
            print(f"[API ERROR] Detalhes do erro: {e}")
            try:
                # Tenta extrair o JSON do corpo da resposta de erro
                error_body = e.response.json()
            except json.JSONDecodeError:
                # Se o corpo do erro não for um JSON válido
                error_body = {"message": e.response.text or "Erro desconhecido na API."}
                
            return e.response.status_code, error_body
        
        except Exception as e:
            # Captura outras exceções (ex: falha de conexão)
            print(f"[API CRITICAL] Erro inesperado ao salvar consumo: {e}")
            return 500, {"message": "Ocorreu um erro interno ao se comunicar com a API."}
