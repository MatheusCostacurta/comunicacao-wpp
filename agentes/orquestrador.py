from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.tools import format_to_tool_messages
from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
from modelos import ConsumoInput
from agentes.ferramentas import all_tools

def executar_agente_principal(mensagem_usuario: str, dados_iniciais: ConsumoInput, llm):
    """
    Aciona o agente orquestrador para buscar os IDs usando as ferramentas disponíveis.
    """
    print("\n--- ETAPA 2: Acionando o Agente Orquestrador para buscar IDs (Método Robusto) ---")

    llm_with_tools = llm.bind_tools(all_tools)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é um assistente especialista em registros agrícolas.
        Sua tarefa é usar as ferramentas disponíveis para encontrar os IDs corretos para cada item mencionado pelo usuário.

        - Para o produto, use a ferramenta 'buscar_produto_por_nome' com o nome do produto extraído.
        - Para talhão e máquina, use as ferramentas 'buscar_talhoes_disponiveis' e 'buscar_maquinas_disponiveis', e então encontre o item correto na lista retornada.

        Analise as listas e encontre os IDs correspondentes aos itens nos dados iniciais.
         
        Quando tiver todos os IDs, responda DIRETAMENTE com o objeto JSON final. Não invente ou chame outras ferramentas. Apenas forneça o JSON como sua resposta final
        - Dados Iniciais Extraídos: {dados_iniciais}
        - O usuário disse: {input}"""),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = (
        {
            "input": lambda x: x["input"],
            "dados_iniciais": lambda x: x["dados_iniciais"],
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
        "dados_iniciais": dados_iniciais.dict()
    })

    return resultado.get("output", "Não foi possível determinar a resposta final.")