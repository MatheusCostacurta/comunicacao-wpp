from datetime import date
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM
from src.comunicacao_wpp_ia.dominio.objetos.consumo_informado import ConsumoInformado
from src.comunicacao_wpp_ia.dominio.servicos.consumo.validador_infos_para_consumo import ValidadorInformacoesParaConsumo
from src.comunicacao_wpp_ia.dominio.utilitarios.string import StringUtilidade

class FabricaConsumoInformado:
    """
    Fábrica responsável por criar um objeto ConsumoInformado a partir de texto não estruturado.
    Encapsula a lógica de extração inicial via LLM e a validação de completude.
    """
    def __init__(self, llm: ServicoLLM):
        self._llm = llm

    @staticmethod
    def __obter_prompt_sistema() -> str:
        return """
            Você é um assistente especialista em extrair informações de consumo agrícola a partir de um texto. 
            Sua tarefa é preencher os campos do modelo de dados com base na mensagem do usuário e no histórico.

            Siga estas regras estritamente:
            1.  **Produtos:** Crie uma lista em `produtos_mencionados`. Para cada produto (insumo químico, fertilizante), adicione um objeto com seu `nome` e `quantidade`.
                - Ex: "Boxer 1, Convicto 13" -> `produtos_mencionados: [{{"nome": "Boxer", "quantidade": "1"}}, {{"nome": "Convicto", "quantidade": "13"}}]`
            2.  **Máquinas:** Crie uma lista em `maquinas_mencionadas`. Para cada máquina, adicione um objeto com seu `nome` e, se disponíveis, `horimetro_inicio`/`horimetro_fim` ou quantidade andada/utilizada.
            3.  **Locais:** Extraia `talhoes_mencionados` e/ou `propriedades_mencionadas` e/ou `plantios_mencionados` como listas de strings.
                - Ex: "no talhão A e B" -> `talhoes_mencionados: ["A", "B"]`
                - Ex: "na fazenda C" -> `propriedades_mencionadas: ["C"]`
                - Ex: "no plantio D" -> `plantios_mencionados: ["D"]`
            4.  **Tipo de Rateio:** Determine o `tipo_rateio` com base na seguinte prioridade:
                - Se a mensagem mencionar um ou mais talhões/glebas e/ou plantios, o tipo é 'plantio'. Ignore qualquer menção à fazenda/propriedade no mesmo comando.
                - Se a mensagem mencionar APENAS uma ou mais fazendas/propriedades, o tipo é 'propriedade'.
            5.  **Data:** Extraia a `data_mencionada` como uma string EXATAMENTE como o usuário falou (ex: "ontem", "dia 20", "20/07", "24 de julho").
            6.  **Safra:** A safra pode ser mencionada apenas através de numeros (ex: 23/24, 2023/2024, 24/24 ou 24)
            7.  Se algum campo(produtos_mencionados, propriedades_mencionadas, talhoes_mencionados, plantios_mencionados, maquinas_mencionadas) não for mencionado, seu valor deve ser [].
            7.1. Se o usuário indicar que **não usou** uma máquina (ex: "aplicação manual", "sem trator"), preencha o campo `maquinas_mencionadas` com o valor [].
            8.  Se algum campo(ponto_estoque_mencionado, data_mencionada, safra_mencionada, id_responsavel, tipo_rateio) não for mencionado, seu valor deve ser nulo (None).
        """

    @staticmethod
    def __obter_mensagem_usuario() -> str:
        return """
            Analise o histórico e a nova mensagem para extrair as informações de consumo.

            Histórico da Conversa:
            {historico}

            Nova Mensagem do Usuário:
            '{mensagem}'
        """

    def criar_de_mensagem(self, mensagem_usuario: str, historico: list) -> (str | ConsumoInformado):
        """
        Usa o LLM para fazer uma extração estruturada rápida. Se um campo obrigatório não for extraído, formula a pergunta para o usuário.
        """
        print("--- ETAPA 1: Checando informações obrigatórias ---")

        prompt_sistema = self.__obter_prompt_sistema()
        prompt_usuario = self.__obter_mensagem_usuario()

        historico_formatado = "\n".join(f"{m['role']}: {m['content']}" for m in historico)
        
        agente = self._llm.criar_agente(prompt_sistema, prompt_usuario, ConsumoInformado) 
        dados_extraidos = agente.executar({"mensagem": mensagem_usuario, "historico": historico_formatado})

        print(f"Dados extraídos na checagem inicial: {dados_extraidos}")

        # Converte a data mencionada (string) para um objeto de data completo
        dados_extraidos.data_mencionada = StringUtilidade.para_data(dados_extraidos.data_mencionada)
        if not dados_extraidos.data_mencionada:
            dados_extraidos.data_mencionada = date.today()

        eh_valido, perguntas_faltantes = ValidadorInformacoesParaConsumo.validar(dados_extraidos)

        if not eh_valido:
            return "Para registrar o consumo, preciso de mais algumas informações: " + " ".join(perguntas_faltantes)
        else:
            return dados_extraidos