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

        campos_obrigatorios = {
            "produtos": consumo.produtos,
            "id_ponto_estoque": consumo.id_ponto_estoque,
            "id_safra": consumo.id_safra,
            "data_aplicacao": consumo.data_aplicacao,
            "tipo_rateio": consumo.tipo_rateio
        }
        campos_faltando = [campo for campo, valor in campos_obrigatorios.items() if not valor]
        if campos_faltando:
            msg_erro = f"Parâmetros obrigatórios ausentes: {', '.join(campos_faltando)}."
            return 400, json.dumps({"status_code": 400, "message": msg_erro})
        
        rateio_payload = {
            "atividade_id": 1, # TODO: Ajustar atividade conforme necessário
            "safra_id": consumo.id_safra,
            "epoca": "SAFRA", # TODO: Remover dps
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
                    # TODO: Validar a lógica de cálculo do horímetro
                    imobilizado_item["quantidade_horimetro_hodometro"] = maquina.horimetro_fim - maquina.horimetro_inicio
                lista_imobilizados.append(imobilizado_item)

        # Montagem do payload principal do consumo
        consumo_payload = {
            "data": consumo.data_aplicacao.strftime('%d/%m/%Y') if hasattr(consumo.data_aplicacao, 'strftime') else consumo.data_aplicacao,
            "responsavel_id": consumo.id_responsavel,
            "ponto_estoque_id": consumo.id_ponto_estoque,
            "tipo_operacao_id": None, # TODO: Adicionar lógica se necessário
            "observacao": "Consumo registrado via WhatsApp",
            "rateio": rateio_payload,
            "lista_imobilizados": lista_imobilizados,
            "lista_produtos": [p.dict() for p in consumo.produtos]
        }
        
        # Estrutura final para a API
        dados_para_salvar = {
            "produtor_id": produtor_id,
            "consumo": consumo_payload
        }

        print("Dados preparados para salvar consumo (nova estrutura):", json.dumps(dados_para_salvar, indent=4))
        
        status_code, response_body = self.repositorio.salvar(
            produtor_id=produtor_id,
            dados_consumo=dados_para_salvar
        )
        
        # Tratamento da resposta da API
        message = response_body.get("message", response_body.get("mensagem", "Ocorreu um erro desconhecido."))
        
        print(f"[SAVER] Resultado da API: StatusCode={status_code}, Mensagem='{message}'")
        return status_code, message
