import json
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM
from src.comunicacao_wpp_ia.aplicacao.portas.memorias import ServicoMemoria
from src.comunicacao_wpp_ia.dominio.modelos.consumo import Consumo
from src.comunicacao_wpp_ia.aplicacao.servicos.checar_informacoes import checar_informacoes_faltantes
from src.comunicacao_wpp_ia.aplicacao.servicos.orquestrador import Orquestrador
from src.comunicacao_wpp_ia.aplicacao.servicos.validar_intencao import validar_intencao_do_usuario
from src.comunicacao_wpp_ia.aplicacao.dtos.dados_remetente import DadosRemetente

def processar_mensagem(mensagem: str, numero_telefone: str, memoria: ServicoMemoria, llm: ServicoLLM):
    """
    Orquestra o fluxo de processamento da mensagem,
    chamando os agentes em sequência e gerenciando a memória.
    """
    print(f"\n--- INICIANDO PROCESSAMENTO PARA: '{mensagem}' (Remetente: {numero_telefone}) ---")

    produtor_id = 1  # Simulando a busca do ID do produtor. Na prática, isso deve ser obtido de uma API ou banco de dados.
    if not produtor_id:
        print("[ERROR] Não foi possível encontrar o id do produtor para o numero de telefone na conversa.")
        print(f"Resposta para o usuário: Não foi possível identificar o produtor associado ao número {numero_telefone}.")
        return
    remetente = DadosRemetente(produtor_id=produtor_id, numero_telefone=numero_telefone)  

    estado_conversa = memoria.obter_estado(numero_telefone)
    historico = estado_conversa["historico"]

    resultado_validacao = validar_intencao_do_usuario(mensagem, historico, llm)
    if not resultado_validacao.intencao_valida:
        print("\n--- RESULTADO FINAL (INTENÇÃO MALICIOSA/INVÁLIDA) ---")
        # Não damos detalhes do erro para o usuário.
        resposta_usuario = "Desculpe, só posso processar registros de consumo. Para outras solicitações, entre em contato com o suporte."
        print(f"Resposta para o usuário: {resposta_usuario}")
        #? Enviar a má intenção para o amplitude para análise
        return
    
    resultado_checagem = checar_informacoes_faltantes(mensagem, historico, llm)
    
    if isinstance(resultado_checagem, str):
        print("\n--- RESULTADO FINAL (FALTAM DADOS) ---")
        print(f"Resposta para o usuário: {resultado_checagem}")
        
        historico.append({"role": "user", "content": mensagem})
        historico.append({"role": "assistant", "content": resultado_checagem})
        memoria.salvar_estado(numero_telefone, historico)
        return

    if isinstance(resultado_checagem, Consumo):
        orquestrador = Orquestrador(llm)
        resultado_agente_str = orquestrador.executar(remetente, mensagem, resultado_checagem, historico)
                
        try:
            # Tenta decodificar o resultado como JSON. Se funcionar, é uma operação de salvamento.
            resultado_api = json.loads(resultado_agente_str)
            
            print(f"\n--- RESULTADO DA OPERAÇÃO DE SALVAMENTO ---")
            print(f"Resposta da API: {resultado_api}")

            status_code = resultado_api.get("status_code")
            mensagem_api = resultado_api.get("message")

            if status_code == 200:
                print("Operação bem-sucedida (Status 200). Limpando o histórico da conversa.")
                memoria.limpar_memoria_conversa(numero_telefone)
                resposta_usuario = "Seu registro foi salvo com sucesso!"
            else:
                print(f"Operação falhou (Status {status_code}). Mantendo o histórico para correção.")
                resposta_usuario = mensagem_api
                historico.append({"role": "user", "content": mensagem})
                historico.append({"role": "assistant", "content": resposta_usuario})
                memoria.salvar_estado(numero_telefone, historico)

        except json.JSONDecodeError:
            # Se falhar a decodificação, é a pergunta de desambiguação do agente.
            print("\n--- RESULTADO FINAL (AMBIGUIDADE DETECTADA, AGUARDANDO USUÁRIO) ---")
            resposta_usuario = resultado_agente_str
            
            # Adiciona a interação ao histórico para que a próxima mensagem do usuário
            # tenha o contexto da pergunta.
            historico.append({"role": "user", "content": mensagem})
            historico.append({"role": "assistant", "content": resposta_usuario})
            memoria.salvar_estado(numero_telefone, historico)

        print(f"Resposta final para o usuário: {resposta_usuario}")