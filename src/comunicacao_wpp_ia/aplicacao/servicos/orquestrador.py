from typing import Any, List
from src.comunicacao_wpp_ia.dominio.modelos.consumo import Consumo
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM

class Orquestrador:
    """
    Este caso de uso orquestra o registro de um consumo utilizando um agente com ferramentas.
    """
    def __init__(self, servico_llm: ServicoLLM, ferramentas: List[Any]):
        self._servico_llm = servico_llm
        self.ferramentas = ferramentas

    def executar(self, mensagem_usuario: str, dados_iniciais: Consumo, historico_conversa: List = None):
        historico_conversa = historico_conversa or []

        prompt_orquestrador = """Você é um assistente especialista em registros agrícolas.
        Sua tarefa é usar as ferramentas disponíveis para encontrar os IDs corretos para cada item mencionado pelo usuário, e após isso, registrar o consumo.

        **REGRAS DE EXECUÇÃO:**
        1.  Use a ferramenta 'buscar_produto_por_nome' para obter listas de produtos similares, em estoque e mais consumidos.
        2.  Analise CUIDADOSAMENTE as 3 listas para identificar o produto correto que corresponde ao mencionado pelo usuário. A prioridade é encontrar um item que já está no histórico de consumo ou em estoque.
        2.1.  **REGRA DE AMBIGUIDADE:** Se, após analisar as listas, você ainda estiver em dúvida entre dois ou mais produtos possíveis (ex: 'Tordon XT' e 'Tordon H'), **NÃO** prossiga e **NÃO** chame a ferramenta 'salvar_registro_consumo'. Sua resposta final **DEVE SER** a pergunta para o usuário, para que ele desfaça a ambiguidade. Por exemplo: "Notei que temos 'Tordon XT' e 'Tordon H'. Qual deles você utilizou?".
        3.  Use as outras ferramentas ('buscar_talhoes_disponiveis', 'buscar_maquinas_disponiveis') para encontrar o ID correspondente aos itens nos dados iniciais.
        4.  Como passo final, e apenas se todas as informações estiverem confirmadas, chame a ferramenta 'salvar_registro_consumo'.
        5.  A resposta da ferramenta 'salvar_registro_consumo' contém 'status_code' e 'message'. Se você chamar essa ferramenta, sua resposta final **DEVE** ser um objeto JSON válido contendo APENAS esses dois campos.
        5.1. Exemplo de Resposta caso chegue ao passo final -> "status_code": 200, "message": "Consumo registrado com sucesso."
         
        - Dados Iniciais Extraídos: {dados_iniciais}
        - O usuário disse: {input}
        - Histórico da conversa até agora: {historico}"""

        agente_com_ferramentas = self._servico_llm.criar_agente_com_ferramentas(prompt_template=prompt_orquestrador, ferramentas=self.ferramentas)
        entradas_agente = {
            "input": mensagem_usuario,
            "dados_iniciais": dados_iniciais.dict(),
            "historico": historico_conversa
        }
        resultado = agente_com_ferramentas.executar(entradas_agente)
        return resultado