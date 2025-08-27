import re
from datetime import date, timedelta
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM
from src.comunicacao_wpp_ia.dominio.modelos.consumo import Consumo
from src.comunicacao_wpp_ia.dominio.servicos.validador_consumo import ValidadorConsumo

def __obter_prompt_sistema() -> str:
    return """
        Você é um assistente especialista em extrair informações de consumo agrícola a partir de um texto. 
        Sua tarefa é preencher os campos do modelo de dados com base na mensagem do usuário e no histórico.

        Siga estas regras estritamente:
        1.  **Produtos:** Crie uma lista em `produtos_mencionados`. Para cada produto (insumo químico, fertilizante), adicione um objeto com seu `nome` e `quantidade`.
            - Ex: "Boxer 1, Convicto 13" -> `produtos_mencionados: [{{"nome": "Boxer", "quantidade": "1"}}, {{"nome": "Convicto", "quantidade": "13"}}]`
        2.  **Máquinas:** Crie uma lista em `maquinas_mencionadas`. Para cada máquina, adicione um objeto com seu `nome` e, se disponíveis, `horimetro_inicio` e `horimetro_fim`.
        3.  **Locais:** Extraia `talhoes_mencionados` e/ou `propriedades_mencionadas` como listas de strings.
            - Ex: "no talhão A e B" -> `talhoes_mencionados: ["A", "B"]`
            - Ex: "na fazenda C" -> `propriedades_mencionadas: ["C"]`
        4.  **Tipo de Rateio:** Determine o `tipo_rateio` com base na seguinte prioridade:
            - Se a mensagem mencionar um ou mais talhões/glebas, o tipo é 'talhao'. Ignore qualquer menção à fazenda/propriedade no mesmo comando.
            - Se a mensagem mencionar APENAS uma ou mais fazendas/propriedades, o tipo é 'propriedade'.
        5.  **Data:** Extraia a `data_mencionada` como uma string EXATAMENTE como o usuário falou (ex: "ontem", "dia 20", "20/07", "24 de julho").
        6.  **Safra:** A safra pode ser mencionada apenas através de numeros (ex: 23/24, 2023/2024, 24/24 ou 24)
        7.  Se um campo não for mencionado, seu valor deve ser nulo (null).
        7.1. Se o usuário indicar que **não usou** uma máquina (ex: "aplicação manual", "sem trator"), preencha o campo `maquina_mencionada` com o valor nulo (null).
    """

def _parse_data_mencionada(data_str: str) -> date:
    """
    Converte uma string de data (parcial ou completa) em um objeto de data.
    Preenche as partes faltantes com a data atual.
    """
    hoje = date.today()

    if not data_str or not isinstance(data_str, str):
        return hoje

    data_str_lower = data_str.lower()
    if "hoje" in data_str_lower:
        return hoje
    if "ontem" in data_str_lower:
        return hoje - timedelta(days=1)

    # Tenta padrão "24 de julho"
    match = re.search(r"(\d{1,2})\s+de\s+([a-zA-Z]+)", data_str_lower)
    if match:
        dia_str, mes_nome = match.groups()
        dia = int(dia_str)
        meses = {
            "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
            "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
        }
        mes = meses.get(mes_nome)
        if mes:
            try:
                return date(hoje.year, mes, dia)
            except ValueError:
                pass

    # Tenta padrão dd/mm/yyyy ou dd-mm-yyyy
    match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", data_str)
    if match:
        dia, mes, ano = map(int, match.groups())
        if ano < 100:
            ano += 2000
        try:
            return date(ano, mes, dia)
        except ValueError:
            pass

    # Tenta padrão dd/mm ou dd-mm
    match = re.search(r"(\d{1,2})[/-](\d{1,2})", data_str)
    if match:
        dia, mes = map(int, match.groups())
        try:
            return date(hoje.year, mes, dia)
        except ValueError:
            pass

    # Tenta padrão para apenas o dia
    numeros = re.findall(r"\d+", data_str)
    if numeros:
        dia = int(numeros[0])
        if 1 <= dia <= 31:
            try:
                return date(hoje.year, hoje.month, dia)
            except ValueError:
                pass

    return hoje

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
    Usa o LLM para fazer uma extração estruturada rápida. Se um campo obrigatório não for extraído, formula a pergunta para o usuário.
    """
    print("--- ETAPA 1: Checando informações obrigatórias ---")

    prompt_sistema = __obter_prompt_sistema()
    prompt_usuario = __obter_mensagem_usuario()

    historico_formatado = "\n".join(f"{m['role']}: {m['content']}" for m in historico)
    
    agente = llm.criar_agente(prompt_sistema, prompt_usuario, Consumo) 
    dados_extraidos = agente.executar({"mensagem": mensagem_usuario, "historico": historico_formatado})

    print(f"Dados extraídos na checagem inicial: {dados_extraidos}")

    # Converte a data mencionada (string) para um objeto de data completo
    dados_extraidos.data_mencionada = _parse_data_mencionada(dados_extraidos.data_mencionada)
    if not dados_extraidos.data_mencionada:
        dados_extraidos.data_mencionada = date.today()

    eh_valido, perguntas_faltantes = ValidadorConsumo.validar(dados_extraidos)

    if not eh_valido:
        return "Para registrar o consumo, preciso de mais algumas informações: " + " ".join(perguntas_faltantes)
    else:
        return dados_extraidos