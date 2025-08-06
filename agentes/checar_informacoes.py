from typing import List
from langchain_core.prompts import ChatPromptTemplate
from modelos import ConsumoInput

def checar_informacoes_faltantes(mensagem_usuario: str, campos_obrigatorios: List[str], llm) -> (str | ConsumoInput):
    """
    Usa o LLM para fazer uma extração estruturada rápida.
    Se um campo obrigatório não for extraído, formula a pergunta para o usuário.
    """
    print("--- ETAPA 1: Checando informações obrigatórias ---")
    structured_llm = llm.with_structured_output(ConsumoInput, include_raw=False)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente que extrai informações de uma mensagem. Extraia os seguintes campos do texto do usuário."),
        ("human", "{mensagem}")
    ])
    chain = prompt | structured_llm
    dados_extraidos = chain.invoke({"mensagem": mensagem_usuario})
    print(f"Dados extraídos na checagem inicial: {dados_extraidos}")

    campos_faltantes = []
    mapa_perguntas = {
        "produto_mencionado": "Qual foi o produto utilizado?",
        "quantidade": "Qual foi a quantidade consumida?",
        "talhao_mencionado": "Em qual talhão ou área foi feita a aplicação?",
        "maquina_mencionada": "Qual máquina foi utilizada na operação?",
    }

    for campo in campos_obrigatorios:
        if not getattr(dados_extraidos, campo):
            campos_faltantes.append(mapa_perguntas[campo])

    if campos_faltantes:
        return "Para registrar o consumo, preciso de mais algumas informações: " + " ".join(campos_faltantes)
    else:
        return dados_extraidos