import json
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM
from src.comunicacao_wpp_ia.aplicacao.portas.memorias import ServicoMemoriaConversa
from src.comunicacao_wpp_ia.dominio.modelos.consumo import Consumo
from src.comunicacao_wpp_ia.aplicacao.servicos.checar_informacoes import checar_informacoes_faltantes
from src.comunicacao_wpp_ia.aplicacao.servicos.orquestrador import Orquestrador
from src.comunicacao_wpp_ia.aplicacao.servicos.validar_intencao import validar_intencao_do_usuario
from src.comunicacao_wpp_ia.aplicacao.dtos.dados_remetente import DadosRemetente
from src.comunicacao_wpp_ia.dominio.repositorios.repositorio_remetente import RepositorioRemetente

class ServicoConversa:
    """
    Serviço de aplicação responsável por orquestrar o fluxo de uma conversa.
    """
    def __init__(self, memoria: ServicoMemoriaConversa, llm: ServicoLLM, repo_remetente: RepositorioRemetente):
        self._memoria = memoria
        self._llm = llm
        self._repo_remetente = repo_remetente

def obter_remetente(self, telefone: str) -> DadosRemetente:
    """
    Busca os dados do remetente (produtor) com base no número de telefone.
    """
    print(f"\n[API MOCK] Buscando produtor pelo telefone {telefone}...")
    remetente = self._repo_remetente.buscar_remetente_por_telefone(telefone)
    
    if not remetente:
        print(f"[ERROR] Não foi possível encontrar um produtor associado ao número {telefone}.")
        return None
    
    return remetente


def processar_mensagem(self, mensagem: str, remetente: DadosRemetente):
    """
    Orquestra o fluxo de processamento da mensagem,
    chamando os agentes em sequência e gerenciando a memória.
    """
    print(f"\n--- INICIANDO PROCESSAMENTO PARA: '{mensagem}' (Remetente: {remetente.numero_telefone}) ---")

    estado_conversa = self._memoria.obter_estado(remetente.numero_telefone)
    historico = estado_conversa["historico"]

    resultado_validacao = validar_intencao_do_usuario(mensagem, historico, self._llm)
    if not resultado_validacao.intencao_valida:
        print("\n--- RESULTADO FINAL (INTENÇÃO MALICIOSA/INVÁLIDA) ---")
        # Não damos detalhes do erro para o usuário.
        resposta_usuario = "Desculpe, só posso processar registros de consumo. Para outras solicitações, entre em contato com o suporte."
        print(f"Resposta para o usuário: {resposta_usuario}")
        #? Enviar a má intenção para o amplitude para análise
        return
    
    resultado_checagem = checar_informacoes_faltantes(mensagem, historico, self._llm)
    
    if isinstance(resultado_checagem, str):
        print("\n--- RESULTADO FINAL (FALTAM DADOS) ---")
        print(f"Resposta para o usuário: {resultado_checagem}")
        
        historico.append({"role": "user", "content": mensagem})
        historico.append({"role": "assistant", "content": resultado_checagem})
        self._memoria.salvar_estado(remetente.numero_telefone, historico)
        return

    if isinstance(resultado_checagem, Consumo):
        orquestrador = Orquestrador(self._llm)
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
                self._memoria.limpar_memoria_conversa(remetente.numero_telefone)
                resposta_usuario = "Seu registro foi salvo com sucesso!"
            else:
                print(f"Operação falhou (Status {status_code}). Mantendo o histórico para correção.")
                resposta_usuario = mensagem_api
                historico.append({"role": "user", "content": mensagem})
                historico.append({"role": "assistant", "content": resposta_usuario})
                self._memoria.salvar_estado(remetente.numero_telefone, historico)

        except json.JSONDecodeError:
            # Se falhar a decodificação, é a pergunta de desambiguação do agente.
            print("\n--- RESULTADO FINAL (AMBIGUIDADE DETECTADA, AGUARDANDO USUÁRIO) ---")
            resposta_usuario = resultado_agente_str
            
            # Adiciona a interação ao histórico para que a próxima mensagem do usuário
            # tenha o contexto da pergunta.
            historico.append({"role": "user", "content": mensagem})
            historico.append({"role": "assistant", "content": resposta_usuario})
            self._memoria.salvar_estado(remetente.numero_telefone, historico)

        print(f"Resposta final para o usuário: {resposta_usuario}")