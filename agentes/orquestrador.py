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

        1.  Primeiro, use as ferramentas de busca ('buscar_produto_por_nome', 'buscar_talhoes_disponiveis', 'buscar_maquinas_disponiveis') para encontrar o item correto.
        2.  Analise as listas e encontre os IDs correspondentes aos itens nos dados iniciais.
        3.  Depois, sua tarefa final é chamar a ferramenta 'salvar_registro_consumo' com os IDs e informações que você encontrou.
        4.  A resposta da ferramenta 'salvar_registro_consumo' contém 'status_code' e 'message'. Sua resposta final **DEVE** ser um objeto JSON válido contendo APENAS esses dois campos.
        
        Exemplo de Resposta Final Obrigatória -> "status_code": 200, "message": "Consumo registrado com sucesso."
        
        NÃO adicione nenhum texto, formatação, explicação ou markdown como ```json ... ```. Sua saída final deve ser o JSON puro e nada mais.

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