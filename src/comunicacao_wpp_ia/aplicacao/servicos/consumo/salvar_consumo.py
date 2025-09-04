import json
from typing import Tuple
from src.comunicacao_wpp_ia.aplicacao.dtos.consumo_para_salvar import ConsumoMontado
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_consumo import RepositorioConsumo

class SalvarConsumo:
    """
    Este caso de uso é responsável por orquestrar o salvamento de um consumo.
    Ele formata os dados e chama a ferramenta de salvamento, retornando
    o resultado bruto da API.
    """

    def __init__(self, repositorio: RepositorioConsumo):
        self.repositorio = repositorio

    def executar(self, produtor_id: int, consumo: ConsumoMontado) -> Tuple[int, str]:
        """
        Executa a lógica para salvar o consumo.
        """
        print("Iniciou SalvarConsumo")

        if not all([consumo.produtos, consumo.id_ponto_estoque, consumo.id_safra, consumo.data_aplicacao, consumo.tipo_rateio]):
            msg_erro = "Parâmetros obrigatórios ausentes. Verifique produtos, ponto_estoque, safra, data e rateio."
            return json.dumps({"status_code": 400, "message": msg_erro})
        
        dados_para_salvar = {
            "atividade_id": 1, # TODO: Ajustar atividade conforme necessário
            "ponto_estoque_id": consumo.id_ponto_estoque,
            "safra_id": consumo.id_safra,
            "data": consumo.data_aplicacao.strftime('%d/%m/%Y') if hasattr(consumo.data_aplicacao, 'strftime') else consumo.data_aplicacao if consumo.data_aplicacao else None,
            # "tipo_rateio": tipo_rateio, #! LIBERAR
            "lista_produtos": [p.dict() for p in consumo.produtos]
        }
        
        #! LIBERAR
        # if maquinas: 
        #     lista_imobilizados = []
        #     for maquina in maquinas:
        #         imobilizado_item = {"id": maquina.id}
        #         if maquina.horimetro_inicio is not None and maquina.horimetro_fim is not None:
        #             imobilizado_item["quantidade_horimetro_hodometro"] = maquina.horimetro_fim - maquina.horimetro_inicio # TODO: Mudar lógica
        #         lista_imobilizados.append(imobilizado_item)
        #     dados_para_salvar["lista_imobilizados"] = lista_imobilizados

        #! LIBERAR
        # if ids_talhoes:
        #     dados_para_salvar["lista_rateios"] = ids_talhoes
        # elif ids_propriedades:
        #     dados_para_salvar["lista_rateios"] = ids_propriedades
        # if id_responsavel:
        #     dados_para_salvar["id_responsavel"] = id_responsavel

        # ! FIZ UM MOCK PARA SALVAR ATÉ AJUSTAR A API
        dados_para_salvar["epoca"] = "SAFRA"
        dados_para_salvar["quantidade_horimetro_hodometro"] = 0
        dados_para_salvar["lista_rateios"] = [{"plantio_id": 517}]

        print("Dados preparados para salvar consumo:", dados_para_salvar)
        status_code, response_body = self.repositorio.salvar(
            produtor_id=produtor_id,
            dados_consumo=dados_para_salvar
        )
        
        resultado_final = {
            "status_code": status_code,
            "message": response_body.get("message", "Ocorreu um erro desconhecido.")
        }

        resultado_json_str = json.dumps(resultado_final)
        
        # Converte a string JSON de resposta em um dicionário Python
        try:
            resultado_api = json.loads(resultado_json_str)
            status_code = resultado_api.get("status_code", 500)
            message = resultado_api.get("message", "Erro desconhecido ao processar a resposta da API.")
            
            print(f"[SAVER] Resultado da API: StatusCode={status_code}, Mensagem='{message}'")
            return status_code, message
            
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"[SAVER ERROR] Não foi possível decodificar a resposta da ferramenta de salvamento: {e}")
            return 500, "Ocorreu um erro interno ao tentar salvar o registro."
