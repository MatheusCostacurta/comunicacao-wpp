from typing import Any, List
from src.comunicacao_wpp_ia.dominio.modelos.consumo import Consumo
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM
from src.comunicacao_wpp_ia.aplicacao.dtos.dados_remetente import DadosRemetente

class Orquestrador:
    """
    Este caso de uso orquestra o registro de um consumo utilizando um agente com ferramentas.
    """
    def __init__(self, servico_llm: ServicoLLM):
        self._servico_llm = servico_llm
        self.ferramentas = servico_llm.obter_ferramentas()

    def executar(self, remetente: DadosRemetente, mensagem_usuario: str, dados_iniciais: Consumo, historico_conversa: List = None):
        historico_conversa = historico_conversa or []

        prompt_orquestrador = f"""Você é um assistente especialista em registros agrícolas.
        Sua tarefa é usar as ferramentas disponíveis para encontrar os IDs corretos para cada item mencionado pelo usuário, e após isso, registrar o consumo.

        **REGRAS E ORDEM DE EXECUÇÃO OBRIGATÓRIA:**
        1.  **BUSCAR RESPONSÁVEL:** Use a ferramenta `buscar_responsavel_por_telefone` com o telefone do usuário para encontrar o ID do responsável.
        2.  **BUSCAR PRODUTO:** Use `buscar_produto_por_nome` para obter listas de similares, em estoque e mais consumidos. Analise CUIDADOSAMENTE as 3 listas para identificar o ID do produto correto. A prioridade é encontrar um item que já está no histórico de consumo ou em estoque.
        3.  **BUSCAR PONTO DE ESTOQUE:** Use `buscar_pontos_de_estoque_disponiveis` para encontrar o ID do depósito mencionado.
        4.  **BUSCAR SAFRA:** Use `buscar_safra_disponivel`. Se o usuário mencionou uma safra, passe o nome. Se não, chame a ferramenta sem parâmetros para obter a safra ativa.
        5.  **BUSCAR TALHÃO (se aplicável):** Se o tipo de rateio for 'talhao', use `buscar_talhoes_disponiveis` para encontrar o ID do talhão.
        6.  **BUSCAR MÁQUINA (opcional):** Se uma máquina foi mencionada, use `buscar_maquinas_disponiveis` para encontrar seu ID.
        7.  **REGRA DE AMBIGUIDADE:** Se, em qualquer etapa, você ficar em dúvida entre dois ou mais itens (ex: 'Tordon XT' e 'Tordon H'), **NÃO** prossiga. Sua resposta final **DEVE SER** a pergunta para o usuário, para que ele desfaça a ambiguidade.
        8.  **SALVAR REGISTRO (PASSO FINAL):** Apenas quando tiver TODOS os IDs (responsável, produto, ponto de estoque, safra, talhão), chame a ferramenta `salvar_registro_consumo` com todos os parâmetros. A data deve ser formatada como 'YYYY-MM-DD'.
        9.  Sua resposta final, após chamar `salvar_registro_consumo`, **DEVE** ser um objeto JSON válido contendo apenas os campos 'status_code' e 'message' retornados pela ferramenta.
        9.1. Exemplo de Resposta caso chegue ao passo final -> "status_code": 200, "message": "Consumo registrado com sucesso."

        **LINGUAGEM:**
        1. Responda sempre na linguagem português-br.
         
        **CONTEXTO ATUAL:**
        - O número de telefone do usuário é: {remetente.numero_telefone}
        - Dados Iniciais Extraídos: {{dados_iniciais}}
        - O usuário disse: {{input}}
        - Histórico da conversa até agora: {{historico}}"""

        agente_com_ferramentas = self._servico_llm.criar_agente_com_ferramentas(prompt_template=prompt_orquestrador, ferramentas=self.ferramentas)
        entradas_agente = {
            "input": mensagem_usuario,
            "dados_iniciais": dados_iniciais.dict(),
            # "dados_iniciais": dados_iniciais.model_dump(),
            "historico": historico_conversa
        }
        resultado = agente_com_ferramentas.executar(entradas_agente)
        return resultado