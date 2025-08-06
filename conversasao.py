from langchain_groq import ChatGroq
from modelos import ConsumoInput
from agentes.checar_informacoes import checar_informacoes_faltantes
from agentes.orquestrador import executar_agente_principal

def processar_mensagem(mensagem: str):
    """
    Orquestra o fluxo de processamento da mensagem,
    chamando os agentes em sequência.
    """
    print(f"\n--- INICIANDO PROCESSAMENTO PARA: '{mensagem}' ---")
    campos_obrigatorios = ["produto_mencionado", "quantidade", "talhao_mencionado"]
    llm = ChatGroq(model_name="llama3-70b-8192", temperature=0)
    
    # Etapa 1: Checar se falta alguma informação
    resultado_checaem = checar_informacoes_faltantes(mensagem, campos_obrigatorios, llm)
    
    if isinstance(resultado_checaem, str):
        print("\n--- RESULTADO FINAL (FALTAM DADOS) ---")
        print(f"Resposta para o usuário: {resultado_checaem}")
        return

    # Etapa 2: Se todas as informações estiverem presentes, acionar o agente principal
    if isinstance(resultado_checaem, ConsumoInput):
        resultado_final = executar_agente_principal(mensagem, resultado_checaem, llm)
        print("\n--- RESULTADO FINAL (OBJETO MONTADO) ---")
        print(resultado_final)