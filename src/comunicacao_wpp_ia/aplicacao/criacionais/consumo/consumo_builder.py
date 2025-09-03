from typing import List
from src.comunicacao_wpp_ia.dominio.modelos.consumo import Consumo
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM
from src.comunicacao_wpp_ia.dominio.modelos.dados_remetente import DadosRemetente

class ConsumoBuilder:
    """
    Este caso de uso orquestra o registro de um consumo utilizando um agente com ferramentas.
    """
    def __init__(self, servico_llm: ServicoLLM):
        self._servico_llm = servico_llm
        self.ferramentas = servico_llm.obter_ferramentas()

    def executar(self, remetente: DadosRemetente, mensagem_usuario: str, dados_iniciais: Consumo, historico_conversa: List = None):
        historico_conversa = historico_conversa or []

        prompt_orquestrador = f"""Você é um assistente especialista em registros agrícolas e seu objetivo é registrar um consumo.
        Sua tarefa é usar as ferramentas disponíveis para encontrar os IDs corretos para cada item mencionado pelo usuário, fazer perguntas caso necessário, e após isso, registrar o consumo.

        1.  **Análise Inicial:**
            -   Você recebeu estes dados iniciais: {{dados_iniciais}}.
            -   O telefone do usuário é: `{remetente.numero_telefone}`.
            -   A mensagem do usuário é: {{input}}
            -   O histórico da conversa é: {{historico}}

        2.  **Fase de Coleta de IDs (Use as Ferramentas):**
            -   Sua missão é preencher todos os IDs necessários para o registro. Use as seguintes ferramentas para encontrar cada um:
            -   **Responsável:** Encontre o ID usando `buscar_responsavel_por_telefone`.
            -   **Produto:** Encontre o ID usando `buscar_produto_por_nome`.
            -   **Ponto de Estoque:** Encontre o ID usando `buscar_pontos_de_estoque_disponiveis`.
            -   **Talhão:** Encontre o ID usando `buscar_talhoes_disponiveis`.
            -   **Propriedade:** Encontre o ID usando `buscar_propriedades_disponiveis`.
            -   **Safra:** Encontre o ID da safra usando `buscar_safra_disponivel` (chame sem parâmetros se o usuário não especificou uma).
            -   **Máquina:** Encontre o ID da maquina usando `buscar_maquinas_disponiveis` (usuário pode ter enviado nome ou número de série).

        3.  **Fase de Decisão:**
            -   **Ambiguidade:** Se alguma busca retornar múltiplos resultados e você não tiver certeza de qual usar (ex: dois produtos com nomes parecidos), **PARE** a coleta e pergunte ao usuário para esclarecer. Sua resposta final deve ser apenas a pergunta.

        5.  **Fase Final (Salvar):**
            -   Use a ferramenta `salvar_registro_consumo` com todos os IDs que você coletou.
            -   Sua resposta final **DEVE** ser o JSON exato retornado por esta ferramenta. Não adicione nenhuma outra palavra.

        Responda sempre em português (Brasil)."""

        agente_com_ferramentas = self._servico_llm.criar_agente_com_ferramentas(prompt_template=prompt_orquestrador, ferramentas=self.ferramentas)
        entradas_agente = {
            "input": mensagem_usuario,
            "dados_iniciais": dados_iniciais.dict(),
            # "dados_iniciais": dados_iniciais.model_dump(),
            "historico": historico_conversa
        }
        resultado = agente_com_ferramentas.executar(entradas_agente)
        return resultado