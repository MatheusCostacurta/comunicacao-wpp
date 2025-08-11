import json
from langchain_groq import ChatGroq
from modelos import ConsumoInput
from agentes.checar_informacoes import checar_informacoes_faltantes
from agentes.orquestrador import executar_agente_principal
from agentes.validar_intencao import validar_intencao_do_usuario
from memoria import GerenciadorMemoria

def processar_mensagem(mensagem: str, numero_telefone: str, memoria: GerenciadorMemoria, llm: ChatGroq):
    """
    Orquestra o fluxo de processamento da mensagem,
    chamando os agentes em sequência e gerenciando a memória.
    """
    print(f"\n--- INICIANDO PROCESSAMENTO PARA: '{mensagem}' (Remetente: {numero_telefone}) ---")
    
    estado_conversa = memoria.obter_estado(numero_telefone)
    historico = estado_conversa["historico"]
    
    historico_para_analise = historico + [{"role": "user", "content": mensagem}]
    texto_completo_conversa = "\n".join(m["content"] for m in historico_para_analise)

    campos_obrigatorios = ["produto_mencionado", "quantidade", "talhao_mencionado"]

    # --- ETAPA 0: VALIDAÇÃO DE SEGURANÇA ---
    resultado_validacao = validar_intencao_do_usuario(mensagem, llm)
    if not resultado_validacao.intencao_valida:
        print("\n--- RESULTADO FINAL (INTENÇÃO MALICIOSA/INVÁLIDA) ---")
        # Não damos detalhes do erro para o usuário.
        resposta_usuario = "Desculpe, só posso processar registros de consumo. Para outras solicitações, entre em contato com o suporte."
        print(f"Resposta para o usuário: {resposta_usuario}")
        #? Enviar a má intenção para o amplitude para análise
        return
    
    resultado_checaem = checar_informacoes_faltantes(texto_completo_conversa, campos_obrigatorios, llm)
    
    if isinstance(resultado_checaem, str):
        print("\n--- RESULTADO FINAL (FALTAM DADOS) ---")
        print(f"Resposta para o usuário: {resultado_checaem}")
        
        historico.append({"role": "user", "content": mensagem})
        historico.append({"role": "assistant", "content": resultado_checaem})
        memoria.salvar_estado(numero_telefone, historico)
        return

    if isinstance(resultado_checaem, ConsumoInput):
        resultado_agente_str = executar_agente_principal(mensagem, resultado_checaem, llm, historico)
        
        try:
            # resultado_api = json.loads(resultado_agente_str.replace("'", "\""))
            resultado_api = json.loads(resultado_agente_str)
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o JSON retornado pelo agente: {resultado_agente_str}")
            resultado_api = {"status_code": 500, "message": "Desculpe, não consegui processar a resposta final. Pode tentar novamente?"}


        print(f"\n--- RESULTADO DA OPERAÇÃO DE SALVAMENTO ---")
        print(f"Resposta da API: {resultado_api}")

        status_code = resultado_api.get("status_code")
        mensagem_api = resultado_api.get("message")

        if status_code == 200:
            print("Operação bem-sucedida (Status 200). Limpando o histórico da conversa.")
            memoria.salvar_estado(numero_telefone, [])
            resposta_usuario = "Seu registro foi salvo com sucesso!"
        else:
            # Qualquer status diferente de 200 é tratado como erro
            print(f"Operação falhou (Status {status_code}). Mantendo o histórico para correção.")
            resposta_usuario = mensagem_api # A mensagem de erro humanizada da API
            
            # Adiciona a interação falha ao histórico para dar contexto na próxima tentativa
            historico.append({"role": "user", "content": mensagem})
            historico.append({"role": "assistant", "content": resposta_usuario})
            memoria.salvar_estado(numero_telefone, historico)

        print(f"Resposta final para o usuário: {resposta_usuario}")