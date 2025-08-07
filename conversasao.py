# conversasao.py
from langchain_groq import ChatGroq
from modelos import ConsumoInput
from agentes.checar_informacoes import checar_informacoes_faltantes
from agentes.orquestrador import executar_agente_principal
from memoria import GerenciadorMemoria

def processar_mensagem(mensagem: str, numero_telefone: str, memoria: GerenciadorMemoria):
    """
    Orquestra o fluxo de processamento da mensagem,
    chamando os agentes em sequência e gerenciando a memória.
    """
    print(f"\n--- INICIANDO PROCESSAMENTO PARA: '{mensagem}' (Remetente: {numero_telefone}) ---")
    
    # Recupera o estado da conversa atual
    estado_conversa = memoria.obter_estado(numero_telefone)
    historico = estado_conversa["historico"]
    
    # Adiciona a mensagem atual ao histórico para ter o contexto completo
    historico_completo = historico + [{"role": "user", "content": mensagem}]

    campos_obrigatorios = ["produto_mencionado", "quantidade", "talhao_mencionado"]
    llm = ChatGroq(model_name="llama3-70b-8192", temperature=0)
    
    # Etapa 1: Checar se falta alguma informação
    # Passa o histórico completo para a checagem
    resultado_checaem = checar_informacoes_faltantes("\n".join(m["content"] for m in historico_completo), campos_obrigatorios, llm)
    
    if isinstance(resultado_checaem, str):
        print("\n--- RESULTADO FINAL (FALTAM DADOS) ---")
        print(f"Resposta para o usuário: {resultado_checaem}")
        
        # Salva o estado da conversa para a próxima interação
        historico.append({"role": "user", "content": mensagem})
        historico.append({"role": "assistant", "content": resultado_checaem})
        memoria.salvar_estado(numero_telefone, historico)
        return

    # Etapa 2: Se todas as informações estiverem presentes, acionar o agente principal
    if isinstance(resultado_checaem, ConsumoInput):
        # Passa o histórico para o agente principal ter mais contexto
        resultado_final = executar_agente_principal(mensagem, resultado_checaem, llm, historico)
        print("\n--- RESULTADO FINAL (OBJETO MONTADO) ---")
        print(resultado_final)
        
        # Limpa o histórico da conversa após o sucesso, pois o ciclo foi concluído
        memoria.salvar_estado(numero_telefone, [])
        print(f"Registro concluído. Memória da conversa com '{numero_telefone}' foi reiniciada.")