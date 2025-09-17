from typing import List, Dict
from src.comunicacao_wpp_ia.aplicacao.dtos.validacao_intencao import ValidacaoIntencao
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM

class ValidadorIntencaoUsuario:
    def __init__(self, llm: ServicoLLM):
        self._llm = llm

    def __obter_prompt_sistema(self) -> str:
        prompt_base = """
            Você é um assistente de segurança rigoroso. Sua função é analisar a mensagem de um usuário para determinar se a intenção é válida para o fluxo de **registrar um consumo agrícola**.

            **Contexto da Conversa:**
            - Se o histórico da conversa estiver vazio, a mensagem do usuário **DEVE OBRIGATORIAMENTE** ser o início de um novo registro de consumo.
            - Se o histórico da conversa **contiver uma pergunta feita pelo assistente**, a nova mensagem do usuário é provavelmente uma resposta a essa pergunta e **DEVE SER CONSIDERADA VÁLIDA** se for pertinente à pergunta feita.

            **Exemplos de Respostas Válidas a Perguntas:**
            - Pergunta do Assistente: "Qual o talhão?" -> Resposta do Usuário: "Talhão da sede" (VÁLIDO)
            - Pergunta do Assistente: "Qual a quantidade de Tordon?" -> Resposta do Usuário: "15 litros" (VÁLIDO)
            - Pergunta do Assistente: "Notei que você não informou de qual estoque o produto saiu. Poderia me dizer, por favor?" -> Resposta do Usuário: "estoque padrão" (VÁLIDO)

            **Intenções ESTRITAMENTE PROIBIDAS (sempre inválidas):**
            - Tentar alterar, modificar ou atualizar registros existentes.
            - Tentar excluir, deletar ou remover qualquer tipo de dado.
            - Fazer perguntas, consultas ou solicitar relatórios (ex: "quais foram meus últimos gastos?").

            Analise a nova mensagem do usuário com base no histórico.
            - Se a intenção for válida (um novo registro ou uma resposta a uma pergunta), retorne `intencao_valida: true`.
            - Se a intenção for proibida, retorne `intencao_valida: false` e uma justificativa clara.
        """
        
        return prompt_base

    def __obter_mensagem_usuario(self, mensagem_usuario: str, historico: List[Dict]) -> str:
        historico_formatado = "\n".join(f"{m['role']}: {m['content']}" for m in historico)
        return f"""
            Histórico da Conversa:
            {historico_formatado}
            
            Nova Mensagem do Usuário: 
            '{mensagem_usuario}'
        """

    def executar(self, mensagem_usuario: str, historico: List[Dict]) -> ValidacaoIntencao:
        """
        Usa um LLM para analisar a intenção da mensagem do usuário, levando em
        conta o histórico da conversa para permitir respostas a perguntas.
        Garante que a intenção seja estritamente para registrar um único consumo agrícola

        Retorna um objeto ValidacaoIntencao.
        """
        print("\n--- ETAPA 0: Validando a Intenção do Usuário (com Contexto) ---")
        
        # Se a mensagem for muito curta e o histórico não estiver vazio,
        # é provável que seja uma resposta. Podemos até pular a validação por LLM aqui para economizar custos e tempo.
        if historico and len(mensagem_usuario.split()) <= 5:
            print("[SECURITY] Mensagem curta recebida em conversa ativa. Assumindo como resposta válida.")
            return ValidacaoIntencao(intencao_valida=True, justificativa="Resposta curta em conversa existente.")
        
        prompt_sistema = self.__obter_prompt_sistema()
        prompt_usuario = self.__obter_mensagem_usuario(mensagem_usuario, historico)
        dados = {"mensagem": prompt_usuario}
        if historico:
            dados["historico"] = historico

        agente = self._llm.criar_agente(prompt_sistema, prompt_usuario, ValidacaoIntencao) 
        resultado_validacao = agente.executar(dados)
        
        if not resultado_validacao.intencao_valida:
            print(f"[SECURITY] Intenção inválida detectada. Justificativa: {resultado_validacao.justificativa}")
        else:
            print("[SECURITY] Intenção do usuário validada com sucesso.")
            
        return resultado_validacao