import json
from typing import Tuple
from src.comunicacao_wpp_ia.dominio.objetos.consumo import Consumo
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_consumo import RepositorioConsumo

class SalvarConsumo:
    """
    Este caso de uso é responsável por orquestrar o salvamento de um consumo.
    Ele formata os dados e chama a ferramenta de salvamento, retornando
    o resultado bruto da API.
    """

    def __init__(self, repositorio: RepositorioConsumo):
        self.repositorio = repositorio

    def executar(self, base_url: str, produtor_id: int, consumo: Consumo) -> Tuple[int, str]:
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
        
        consumo.id_atividade = "MQ==" # TODO: Ajustar atividade conforme necessário
        consumo.epoca = "TODAS"
        consumo.observacao = "Consumo registrado via WhatsApp"
        
        resposta = self.repositorio.enviar(
            base_url=base_url,
            produtor_id=produtor_id,
            consumo=consumo
        )
        
        mensagem_final = ""
        if resposta.status >= 400 and isinstance(resposta.dados, list) and resposta.dados:
            # Concatena os detalhes do erro para uma mensagem clara
            detalhes_erro = " ".join(str(item) for item in resposta.dados)
            mensagem_final = f"{resposta.mensagem}: {detalhes_erro}"
        else:
            # Para casos de sucesso ou erros sem detalhes, usa a mensagem principal
            mensagem_final = resposta.mensagem

        print(f"[SAVER] Resultado da API: StatusCode={resposta.status}, Mensagem='{mensagem_final}'")
        return resposta.status, mensagem_final
