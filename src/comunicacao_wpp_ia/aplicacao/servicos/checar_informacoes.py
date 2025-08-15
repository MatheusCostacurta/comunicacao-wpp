from typing import List
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM
from src.comunicacao_wpp_ia.dominio.modelos.consumo import Consumo
from src.comunicacao_wpp_ia.dominio.servicos.validador_consumo import ValidadorConsumo

def __obter_prompt_sistema() -> str:
    return """
        Você é um assistente especialista em extrair informações de consumo agrícola a partir de um texto. Sua tarefa é preencher os campos do modelo de dados com base na mensagem do usuário.

        Siga estas regras estritamente:
        1.  Extraia `produto_mencionado`, `quantidade`, e `talhao_mencionado`.
        2.  O campo `maquina_mencionada` é opcional. Extraia-o apenas se for explicitamente mencionado.
        3.  Se o usuário indicar que **não usou** uma máquina (ex: "aplicação manual", "sem trator"), preencha o campo `maquina_mencionada` com o valor nulo (null).
        4.  Se um campo obrigatório não estiver na mensagem, seu valor deve ser nulo (null).

        **Exemplo de Extração:**
        - **Mensagem do Usuário:** "anota aí 15 litros de tordon no campo da sede, foi aplicação manual."
         - **Sua Extração:** `{{"produto_mencionado": "tordon", "quantidade": "15 litros", "talhao_mencionado": "campo da sede", "maquina_mencionada": "Nenhuma"}}`
    """

def __obter_mensagem_usuario() -> str:
    return """
        Analise o histórico e a nova mensagem para extrair as informações de consumo.

        Histórico da Conversa:
        {historico}

        Nova Mensagem do Usuário:
        '{mensagem}'
    """

def checar_informacoes_faltantes(mensagem_usuario: str, historico: list, llm: ServicoLLM) -> (str | Consumo):
    """
    Usa o LLM para fazer uma extração estruturada rápida.
    Se um campo obrigatório não for extraído, formula a pergunta para o usuário.
    """
    print("--- ETAPA 1: Checando informações obrigatórias ---")

    prompt_sistema = __obter_prompt_sistema()
    prompt_usuario = __obter_mensagem_usuario()

    historico_formatado = "\n".join(f"{m['role']}: {m['content']}" for m in historico)
    
    agente = llm.criar_agente(prompt_sistema, prompt_usuario, Consumo) 
    dados_extraidos = agente.executar({"mensagem": mensagem_usuario, "historico": historico_formatado})

    print(f"Dados extraídos na checagem inicial: {dados_extraidos}")

    eh_valido, perguntas_faltantes = ValidadorConsumo.validar(dados_extraidos)

    if not eh_valido:
        return "Para registrar o consumo, preciso de mais algumas informações: " + " ".join(perguntas_faltantes)
    else:
        return dados_extraidos