import json
from typing import Dict, Tuple
from requests import HTTPError
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_consumo import RepositorioConsumo
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.clientes_api.agriwin_cliente import AgriwinCliente
from src.comunicacao_wpp_ia.dominio.objetos.api.resposta_api import RespostaApi


class RepoAgriwinConsumo(RepositorioConsumo):
    """
    Adaptador que implementa as interfaces de repositório para o remetente.
    """
    def __init__(self, agriwin_cliente: AgriwinCliente):
        self._cliente = agriwin_cliente
        print("[INFRA] Adaptador do Repositório AgriwinRemetente inicializado.")
    

    def salvar(self, produtor_id: int, dados_consumo: Dict) -> Tuple[int, RespostaApi]:
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
            response = self._cliente.post(endpoint, payload_completo)
            response_body = response.json()
            
            return RespostaApi(
                status=response.status_code,
                mensagem=response_body.get("mensagem", "Operação bem-sucedida."),
                dados=response_body.get("dados")
            )
        except HTTPError as e: # Erros 4xx e 5xx são capturados aqui
            print(f"[API ERROR] Erro ao salvar consumo: {e.response.status_code} - {e.response.text}")
            try:
                error_body = e.response.json()
                return RespostaApi(
                    status=e.response.status_code,
                    mensagem=error_body.get("mensagem", "Erro ao processar requisição."),
                    dados=error_body.get("dados")
                )
            except json.JSONDecodeError: # Se o corpo do erro não for um JSON válido
                return RespostaApi(
                    status=e.response.status_code,
                    mensagem=e.response.text or "Erro desconhecido.",
                    dados=None
                )
        except Exception as e: # Captura outras exceções (ex: falha de conexão)
            print(f"[API CRITICAL] Erro inesperado ao salvar consumo: {e}")
            return RespostaApi(
                status=500,
                mensagem="Ocorreu um erro interno ao se comunicar com o Agriwin.",
                dados=str(e)
            )