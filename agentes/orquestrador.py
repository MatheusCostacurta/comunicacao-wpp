from typing import List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.tools import format_to_tool_messages
from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
from modelos import ConsumoInput
from agentes.ferramentas import all_tools

def executar_agente_principal(mensagem_usuario: str, dados_iniciais: ConsumoInput, llm, historico_conversa: List = None):
    """
    Aciona o agente orquestrador para buscar os IDs usando as ferramentas disponíveis, ao final, salvar o registro.
    """
    print("\n--- ETAPA 2: Acionando o Agente Orquestrador para buscar IDs e salvar (Método Robusto) ---")

    historico_conversa = historico_conversa or []

    llm_with_tools = llm.bind_tools(all_tools)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é um assistente especialista em registros agrícolas.
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
        - Histórico da conversa até agora: {historico}"""),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = (
        {
            "input": lambda x: x["input"],
            "dados_iniciais": lambda x: x["dados_iniciais"],
            "historico": lambda x: x["historico"],
            "agent_scratchpad": lambda x: format_to_tool_messages(x["intermediate_steps"]),
        }
        | prompt
        | llm_with_tools
        | ToolsAgentOutputParser()
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        verbose=True
    )
    
    resultado = agent_executor.invoke({
        "input": mensagem_usuario,
        "dados_iniciais": dados_iniciais.dict(),
        "historico": historico_conversa
    })

    return resultado.get("output", "Não foi possível determinar a resposta final.")