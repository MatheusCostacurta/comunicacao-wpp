from typing import List
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM
from src.comunicacao_wpp_ia.dominio.modelos.consumo import Consumo

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
    return "Analise e extraia as informações do seguinte texto: {mensagem}"

def checar_informacoes_faltantes(mensagem_usuario: str, campos_obrigatorios: List[str], llm: ServicoLLM) -> (str | Consumo):
    """
    Usa o LLM para fazer uma extração estruturada rápida.
    Se um campo obrigatório não for extraído, formula a pergunta para o usuário.
    """
    print("--- ETAPA 1: Checando informações obrigatórias ---")

    prompt_sistema = __obter_prompt_sistema()
    prompt_usuario = __obter_mensagem_usuario()
    
    agente = llm.criar_agente(prompt_sistema, prompt_usuario, Consumo) 
    dados_extraidos = agente.executar({"mensagem": mensagem_usuario})

    print(f"Dados extraídos na checagem inicial: {dados_extraidos}")

    campos_faltantes = []
    mapa_perguntas = {
        "produto_mencionado": "Qual foi o produto utilizado?",
        "quantidade": "Qual foi a quantidade consumida?",
        "talhao_mencionado": "Em qual propriedade ou talhão foi feita a aplicação?",
        "maquina_mencionada": "Qual máquina foi utilizada na operação?",
    }

    for campo in campos_obrigatorios:
        if not getattr(dados_extraidos, campo):
            campos_faltantes.append(mapa_perguntas[campo])

    if campos_faltantes:
        return "Para registrar o consumo, preciso de mais algumas informações: " + " ".join(campos_faltantes)
    else:
        return dados_extraidos