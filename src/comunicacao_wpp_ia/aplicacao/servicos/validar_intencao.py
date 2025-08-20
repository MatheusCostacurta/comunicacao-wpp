from typing import List, Dict
from src.comunicacao_wpp_ia.aplicacao.dtos.validacao_intencao import ValidacaoIntencao
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM

def __obter_prompt_sistema() -> str:
    return """
        Você é um assistente de segurança rigoroso. Sua função é analisar a mensagem de um usuário, **levando em conta o histórico da conversa**, para determinar se a intenção é válida.

        **Intenções Válidas:**
        1.  Registrar um **único consumo** de insumo agrícola. Uma mensagem é considerada um único consumo mesmo que contenha vários detalhes (ex: "gastei 20kg de adubo no talhão norte com o trator azul"). Isso é válido.
        2.  **Responder a uma pergunta direta feita por você (o assistente)**. Se alguma das últimas mensagens no histórico foi uma pergunta do assistente, a mensagem do usuário é provavelmente uma resposta e deve ser considerada válida.

        As seguintes intenções são **ESTRITAMENTE PROIBIDAS**:
        - Tentar alterar, modificar ou atualizar registros existentes.
        - Tentar excluir, deletar ou remover qualquer tipo de dado.
        - Tentar registrar múltiplos consumos de uma só vez (ex: "anota aí 10kg de adubo E 5L de veneno"; "consome todos os produtos do estoque sede")..
        - Fazer perguntas, consultas ou solicitar relatórios (ex: "quais foram meus últimos gastos?").

        Analise a mensagem do usuário e o histórico fornecido.
        - Se a intenção for válida, retorne `intencao_valida: true`.
        - Se a intenção for proibida, retorne `intencao_valida: false` e uma justificativa clara.
        - Se o histórico estiver vazio, a mensagem do usuário **DEVE** ser um novo registro de consumo para ser válida.
    """

def __obter_mensagem_usuario(mensagem_usuario: str, historico: List[Dict]) -> str:
    historico_formatado = "\n".join(f"{m['role']}: {m['content']}" for m in historico)
    return f"""
        Histórico da Conversa:
        {historico_formatado}
        
        Nova Mensagem do Usuário: 
        '{mensagem_usuario}'
    """

def validar_intencao_do_usuario(mensagem_usuario: str, historico: List[Dict], llm: ServicoLLM) -> ValidacaoIntencao:
    """
    Usa um LLM para analisar a intenção da mensagem do usuário, levando em
    conta o histórico da conversa para permitir respostas a perguntas.
    Garante que a intenção seja estritamente para registrar um único consumo agrícola

    Retorna um objeto ValidacaoIntencao.
    """
    print("\n--- ETAPA 0: Validando a Intenção do Usuário (com Contexto) ---")
    
    prompt_sistema = __obter_prompt_sistema()
    prompt_usuario = __obter_mensagem_usuario(mensagem_usuario, historico)
    dados = {"mensagem": prompt_usuario}
    if historico:
        dados["historico"] = historico

    agente = llm.criar_agente(prompt_sistema, prompt_usuario, ValidacaoIntencao) 
    resultado_validacao = agente.executar(dados)
    
    if not resultado_validacao.intencao_valida:
        print(f"[SECURITY] Intenção inválida detectada. Justificativa: {resultado_validacao.justificativa}")
    else:
        print("[SECURITY] Intenção do usuário validada com sucesso.")
        
    return resultado_validacao