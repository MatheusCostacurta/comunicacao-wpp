from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM
from src.comunicacao_wpp_ia.aplicacao.portas.memorias import ServicoMemoriaConversa
from src.comunicacao_wpp_ia.aplicacao.portas.whatsapp import Whatsapp
from src.comunicacao_wpp_ia.dominio.objetos.consumo_informado import ConsumoInformado
from src.comunicacao_wpp_ia.aplicacao.criacionais.consumo.consumo_informado_factory import FabricaConsumoInformado
from src.comunicacao_wpp_ia.aplicacao.criacionais.consumo.consumo_builder import ConsumoBuilder
from src.comunicacao_wpp_ia.aplicacao.servicos.consumo.salvar_consumo import SalvarConsumo
from src.comunicacao_wpp_ia.aplicacao.servicos.remetente.validar_intencao import validar_intencao_do_usuario
from src.comunicacao_wpp_ia.aplicacao.portas.pre_processamento_texto import ServicoPreProcessamento
from src.comunicacao_wpp_ia.dominio.modelos.dados_remetente import DadosRemetente
from src.comunicacao_wpp_ia.aplicacao.dtos.mensagem_recebida import MensagemRecebida
from src.comunicacao_wpp_ia.dominio.objetos.consumo import Consumo
from src.comunicacao_wpp_ia.aplicacao.servicos.consumo.verificar_consumo_montado import verificar_dados_consumo
from src.comunicacao_wpp_ia.aplicacao.servicos.remetente.obter_remetente import ObterRemetente


class ServicoConversa:
    """
    Serviço de aplicação responsável por orquestrar o fluxo de uma conversa.
    """
    def __init__(self, memoria: ServicoMemoriaConversa, llm: ServicoLLM, obter_remetente_service: ObterRemetente, salvar_consumo_service: SalvarConsumo, pre_processador: ServicoPreProcessamento, whatsapp: Whatsapp):
        self._memoria = memoria
        self._llm = llm
        self._obter_remetente_service = obter_remetente_service
        self._pre_processador = pre_processador
        self._salvar_consumo_service = salvar_consumo_service
        self._fabrica_consumo_informado = FabricaConsumoInformado(llm)
        self._whatsapp = whatsapp

    def _encerrar_conversa(self, telefone: str, mensagem_erro: str):
        """
        Limpa a memória da conversa e envia uma mensagem de erro seguida da notificação de encerramento.
        """
        self._memoria.limpar_memoria_conversa(telefone)
        if mensagem_erro:
            self._whatsapp.enviar(telefone, mensagem_erro)
        self._whatsapp.enviar(telefone, "Conversa finalizada.")
        
    def processar_mensagem_recebida(self, mensagem_recebida: MensagemRecebida):
        """
        Ponto de entrada principal. Orquestra a busca do remetente, pré-processamento
        e o fluxo de conversação.
        """
        remetente = self._obter_remetente_service.executar(telefone=mensagem_recebida.telefone_remetente)
        if not remetente:
            print(f"[ERROR] Remetente não encontrado para o telefone: {mensagem_recebida.telefone_remetente}. Encerrando fluxo.")
            mensagem_final = "Não foi possível identificar seu usuário. Por favor, entre em contato com o suporte."
            self._encerrar_conversa(mensagem_recebida.telefone_remetente, mensagem_final)
            return 
        
        conteudo_texto = self._pre_processador.processar(mensagem_recebida)
        if not conteudo_texto:
            print("[SERVICO CONVERSA] Pré-processamento não retornou conteúdo. Encerrando fluxo.")
            mensagem_final = "Não consegui entender sua mensagem. Por favor, tente novamente em texto, áudio ou imagem."
            self._encerrar_conversa(mensagem_recebida.telefone_remetente, mensagem_final)
            return

        self._processar_conteudo_texto(conteudo_texto, remetente)

    def _processar_conteudo_texto(self, mensagem: str, remetente: DadosRemetente):
        """
        Orquestra o fluxo de processamento do conteúdo textual da mensagem.
        """
        print(f"\n--- INICIANDO PROCESSAMENTO PARA: '{mensagem}' (Remetente: {remetente.numero_telefone}) ---")
        estado_conversa = self._memoria.obter_estado(remetente.numero_telefone)
        historico = estado_conversa["historico"]

        # Etapa 0: Validar intenção
        if not self._validar_intencao(mensagem, historico, remetente.numero_telefone):
            return

        # Etapa 1: Extrair dados e checar se faltam informações
        resultado_construcao = self._fabrica_consumo_informado.criar_de_mensagem(mensagem, historico)
        if isinstance(resultado_construcao, str):
            self._responder_e_salvar_historico(remetente.numero_telefone, mensagem, resultado_construcao, historico)
            return

        if isinstance(resultado_construcao, ConsumoInformado):
            # Etapa 2: Construir o objeto de consumo completo
            consumo_informado = resultado_construcao
            resultado_builder = self._construir_consumo(remetente, mensagem, consumo_informado, historico)
            if isinstance(resultado_builder, str): # Builder pediu esclarecimento
                self._responder_e_salvar_historico(remetente.numero_telefone, mensagem, resultado_builder, historico)
                return
            
            if isinstance(resultado_builder, Consumo):
                # Etapa 3: Salvar o consumo e finalizar
                consumo_montado = resultado_builder
                self._salvar_consumo(remetente, mensagem, consumo_montado, historico)

    def _validar_intencao(self, mensagem: str, historico: list, telefone: str) -> bool:
        resultado_validacao = validar_intencao_do_usuario(mensagem, historico, self._llm)
        if not resultado_validacao.intencao_valida:
            print("\n--- RESULTADO FINAL (INTENÇÃO MALICIOSA/INVÁLIDA) ---")
            resposta_usuario = "Desculpe, só posso processar registros de consumo. Para outras solicitações, entre em contato com o suporte."
            #? Enviar a má intenção para o amplitude para análise se estamos errando na validação
            self._whatsapp.enviar(telefone, resposta_usuario)
            return False
        return True
    
    def _construir_consumo(self, remetente: DadosRemetente, mensagem: str, consumo_informado: ConsumoInformado, historico: list):
        """
        Invoca o ConsumoBuilder para coletar todos os IDs e montar o objeto final.
        Retorna um Consumo em caso de sucesso ou uma string (pergunta) em caso de ambiguidade.
        """
        builder_consumo = ConsumoBuilder(self._llm)
        return builder_consumo.executar(remetente, mensagem, consumo_informado, historico)
    
    def _responder_e_salvar_historico(self, telefone: str, mensagem_usuario: str, resposta_assistente: str, historico: list):
        self._whatsapp.enviar(telefone, resposta_assistente)
        historico.append({"role": "user", "content": mensagem_usuario})
        historico.append({"role": "assistant", "content": resposta_assistente})
        self._memoria.salvar_estado(telefone, historico)
    
    def _salvar_consumo(self, remetente: DadosRemetente, mensagem: str, consumo_montado: Consumo, historico: list):
        resultado_verificacao = verificar_dados_consumo(consumo_montado, self._llm)
        if not resultado_verificacao.aprovado:
            print(f"\n--- RESULTADO FINAL (DADOS INCONSISTENTES) ---")
            resposta_usuario = resultado_verificacao.justificativa
            historico.append({"role": "user", "content": mensagem})
            historico.append({"role": "assistant", "content": resposta_usuario})
            self._memoria.salvar_estado(remetente.numero_telefone, historico)
            self._whatsapp.enviar(remetente.numero_telefone, resposta_usuario)
            return

        status_code, mensagem_api = self._salvar_consumo_service.executar(remetente.produtor_id, consumo_montado)
        if status_code == 200:
            self._memoria.limpar_memoria_conversa(remetente.numero_telefone)
            resposta_usuario = "Seu registro foi salvo com sucesso!"
            self._whatsapp.enviar(remetente.numero_telefone, resposta_usuario)
        else:
            #TODO: a resposta pro usuario está vindo dentro do campo 'dados' do json
            resposta_usuario = f"Não foi possível salvar seu registro. Motivo: {mensagem_api}"
            self._responder_e_salvar_historico(remetente.numero_telefone, mensagem, resposta_usuario, historico)