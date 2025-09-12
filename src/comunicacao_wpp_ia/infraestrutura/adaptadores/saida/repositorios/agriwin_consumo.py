import json
from typing import Dict, Tuple
from requests import HTTPError
from src.comunicacao_wpp_ia.dominio.objetos.consumo import Consumo
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
    

    def enviar(self, base_url: str, produtor_id: int, consumo: Consumo) -> Tuple[int, RespostaApi]:
        """
        Envia os dados de consumo para a API Agriwin através de um POST.
        Retorna uma tupla contendo o status_code e o corpo da resposta em JSON.
        """
        endpoint = "/api/v1/consumos"

        rateio_payload = {
            "atividade_id": consumo.id_atividade,
            "safra_id": consumo.id_safra,
            "tipo": None,
            "propriedades": None,
            "plantios": None,
            "culturas": None,
            "lotes": None
        }

        if consumo.tipo_rateio == 'propriedade':
            rateio_payload["tipo"] = "PROPRIEDADE_AGRICOLA"
            rateio_payload["propriedades"] = consumo.ids_propriedades
        elif consumo.tipo_rateio == 'talhao':
            rateio_payload["tipo"] = "PLANTIO"
            rateio_payload["plantios"] = consumo.ids_talhoes

        # Montagem da lista de imobilizados (máquinas)
        lista_imobilizados = None
        if consumo.maquinas:
            lista_imobilizados = []
            for maquina in consumo.maquinas:
                imobilizado_item = {"id": maquina.id}
                if maquina.horimetro_inicio is not None and maquina.horimetro_fim is not None:
                    imobilizado_item["quantidade_horimetro_hodometro"] = maquina.horimetro_fim - maquina.horimetro_inicio
                lista_imobilizados.append(imobilizado_item)

        # ! Preciso criar um tipo de consumoRequest para definir na interface e garantir que o adaptador implemente corretamente
        consumo_payload = {
            "data": consumo.data_aplicacao.strftime('%d/%m/%Y') if hasattr(consumo.data_aplicacao, 'strftime') else consumo.data_aplicacao,
            "responsavel_id": consumo.id_responsavel,
            "ponto_estoque_id": consumo.id_ponto_estoque,
            "tipo_operacao_id": None, # TODO: Adicionar lógica se necessário
            "rateio": rateio_payload,
            "imobilizados": lista_imobilizados,
            "itens": [p.dict() for p in consumo.produtos],
            "observacao": consumo.observacao
        }

        payload_completo = {
            "identificador_produtor": produtor_id,
            "consumo": consumo_payload
        }
        print(f"\n[API] Enviando POST para salvar consumo em {endpoint}: {json.dumps(payload_completo, indent=4)}")

        try:
            response = self._cliente.post(base_url, endpoint, payload_completo)
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