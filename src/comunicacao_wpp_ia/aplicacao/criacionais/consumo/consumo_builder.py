from typing import List, Dict, Any
import json
from src.comunicacao_wpp_ia.aplicacao.dtos.consumo_informado import ConsumoInformado
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM
from src.comunicacao_wpp_ia.dominio.modelos.dados_remetente import DadosRemetente
from src.comunicacao_wpp_ia.aplicacao.dtos.consumo_para_salvar import ConsumoMontado

class ConsumoBuilder:
    """
    Orquestra a COLETA de informações para um consumo, utilizando um agente com ferramentas. Sua responsabilidade termina ao montar o objeto de consumo com todos os IDs encontrados.
    """
    def __init__(self, servico_llm: ServicoLLM):
        self._servico_llm = servico_llm
        self.ferramentas = servico_llm.obter_ferramentas()

    def _criar_prompt(self, remetente: DadosRemetente) -> str:
        return f"""
        Você é um agente especialista em coletar dados agrícolas.
        Sua única missão é usar as ferramentas para encontrar os IDs de todos os itens mencionados pelo usuário e, ao final, montar um objeto JSON estruturado com esses dados.

        **Regras:**
        1.  **Colete Primeiro:** Use as ferramentas para buscar IDs para produtos, talhões, máquinas, etc., com base nos `dados_iniciais`.
        2.  **Seja Resiliente:** Se uma busca não retornar um ID (retornar nulo ou vazio), não tem problema. Continue para o próximo item.
        3.  **Ambiguidade:** O único caso em que você deve parar e fazer uma pergunta é se UMA busca por UM item retornar MÚLTIPLOS resultados possíveis (ex: dois produtos com nomes parecidos).
        3.1 - - Nesse caso, PARE e pergunte ao usuário para esclarecer qual ele quer. Responda sempre em português (Brasil)
        4.  **Formato Final:** Após buscar tudo, sua resposta final DEVE SER APENAS um objeto JSON estruturado com os dados que você encontrou. Use o seguinte formato:
            {{{{
                "produtos": [{{{{ "id": <int>, "quantidade": <float> }}}}],
                "id_ponto_estoque": <int | null>,
                "id_safra": <int | null>,
                "data_aplicacao": "<DD/MM/YYYY>",
                "tipo_rateio": "<'talhao' | 'propriedade'>",
                "ids_talhoes": [<int>],
                "ids_propriedades": [<int>],
                "id_responsavel": <int | null>,
                "maquinas": [{{{{ "id": <int>, "horimetro_inicio": <float | null>, "horimetro_fim": <float | null> }}}}]
            }}}}

        **Dados de Entrada:**
            -   Você recebeu estes dados iniciais: {{dados_iniciais}}.
            -   O telefone do usuário é: `{remetente.numero_telefone}`.
            -   A mensagem do usuário é: {{input}}
            -   O histórico da conversa é: {{historico}}
        """

    def executar(self, remetente: DadosRemetente, mensagem_usuario: str, dados_iniciais: ConsumoInformado, historico_conversa: List = None):
        historico_conversa = historico_conversa or []

        prompt_orquestrador = self._criar_prompt(remetente)

        agente_com_ferramentas = self._servico_llm.criar_agente_com_ferramentas(prompt_template=prompt_orquestrador, ferramentas=self.ferramentas)
        entradas_agente = {
            "input": mensagem_usuario,
            "dados_iniciais": dados_iniciais.dict(),
            "historico": historico_conversa
        }

        resultado_str = agente_com_ferramentas.executar(entradas_agente)
        try:
            dados_json = json.loads(resultado_str)
            consumo_montado = ConsumoMontado.model_validate(dados_json)
            return consumo_montado
        except (json.JSONDecodeError, Exception):
            return resultado_str