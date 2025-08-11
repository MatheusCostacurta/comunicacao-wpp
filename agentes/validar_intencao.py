from langchain_core.prompts import ChatPromptTemplate
from dtos.validacao_intencao import ValidacaoIntencao

def validar_intencao_do_usuario(mensagem_usuario: str, llm) -> ValidacaoIntencao:
    """
    Usa um LLM para analisar a intenção da mensagem do usuário e garantir que ela
    seja estritamente para registrar um único consumo agrícola.

    Retorna um objeto ValidacaoIntencao.
    """
    print("\n--- ETAPA 0: Validando a Intenção do Usuário ---")
    
    structured_llm = llm.with_structured_output(ValidacaoIntencao, include_raw=False)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Você é um assistente de segurança rigoroso. Sua única função é analisar a mensagem de um usuário e determinar se a intenção dele é estritamente para **registrar um único consumo de insumo agrícola**.

        A única intenção válida é relatar um gasto ou uso de um produto. Ex: "gastei 20kg de adubo", "usei 15L de tordon".

        As seguintes intenções são **ESTRITAMENTE PROIBIDAS**:
        - Tentar alterar, modificar ou atualizar registros existentes.
        - Tentar excluir, deletar ou remover qualquer tipo de dado.
        - Tentar registrar múltiplos consumos de uma só vez.
        - Fazer perguntas, consultas ou solicitar relatórios (ex: "quais foram meus últimos gastos?").
        - Tentar iniciar um loop, enviar comandos maliciosos ou qualquer outra operação que não seja o simples registro de um consumo.

        Analise a mensagem do usuário e retorne sua avaliação no formato estruturado.
        - Se a intenção for válida, retorne `intencao_valida: true`.
        - Se a intenção for qualquer uma das proibidas ou algo diferente do permitido, retorne `intencao_valida: false` e uma justificativa clara.
        """),
        ("human", "Mensagem do usuário: '{mensagem}'")
    ])
    
    chain = prompt | structured_llm
    resultado_validacao = chain.invoke({"mensagem": mensagem_usuario})
    
    if not resultado_validacao.intencao_valida:
        print(f"[SECURITY] Intenção INVÁLIDA detectada. Justificativa: {resultado_validacao.justificativa}")
    else:
        print("[SECURITY] Intenção do usuário validada com sucesso.")
        
    return resultado_validacao