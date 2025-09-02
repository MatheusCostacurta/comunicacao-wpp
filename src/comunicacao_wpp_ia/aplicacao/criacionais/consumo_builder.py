from typing import List
from src.comunicacao_wpp_ia.dominio.modelos.consumo import Consumo
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM
from src.comunicacao_wpp_ia.dominio.modelos.dados_remetente import DadosRemetente

class ConsumoBuilder:
    """
    Este caso de uso orquestra o registro de um consumo utilizando um agente com ferramentas.
    """
    def __init__(self, servico_llm: ServicoLLM):
        self._servico_llm = servico_llm
        self.ferramentas = servico_llm.obter_ferramentas()

    def executar(self, remetente: DadosRemetente, mensagem_usuario: str, dados_iniciais: Consumo, historico_conversa: List = None):
        historico_conversa = historico_conversa or []

        prompt_orquestrador = f"""Você é um assistente especialista em registros agrícolas e seu objetivo é registrar um consumo.
        Sua tarefa é usar as ferramentas disponíveis para encontrar os IDs corretos para cada item mencionado pelo usuário, e após isso, registrar o consumo.

        1.  **Análise Inicial:**
            -   Você recebeu estes dados iniciais: {{dados_iniciais}}.
            -   O telefone do usuário é: `{remetente.numero_telefone}`.
            -   A mensagem do usuário é: {{input}}
            -   O histórico da conversa é: {{historico}}

        2.  **Fase de Coleta de IDs (Use as Ferramentas):**
            -   Sua missão é preencher todos os IDs necessários para o registro. Use as seguintes ferramentas para encontrar cada um:
            -   **Responsável:** Encontre o ID usando `buscar_responsavel_por_telefone`.
            -   **Produto:** Encontre o ID usando `buscar_produto_por_nome`.
            -   **Ponto de Estoque:** Encontre o ID usando `buscar_pontos_de_estoque_disponiveis`.
            -   **Talhão:** Encontre o ID usando `buscar_talhoes_disponiveis`.
            -   **Propriedade:** Encontre o ID usando `buscar_propriedades_disponiveis`.
            -   **Safra:** Encontre o ID da safra ativa usando `buscar_safra_disponivel` (chame sem parâmetros se o usuário não especificou uma).
            -   **Máquina (Opcional):** Se uma máquina/imobilizado for mencionada (nome ou número de série), encontre o ID com `buscar_maquinas_disponiveis`; Se o usuário mencionou uma máquina mas não informou o horímetro (ou odômetro) inicial e final, **PARE** e pergunte por essa informação. Ex: "Qual era o horímetro inicial e final do trator JD6110J?".

        3.  **Fase de Decisão:**
            -   **Ambiguidade:** Se alguma busca retornar múltiplos resultados e você não tiver certeza de qual usar (ex: dois produtos com nomes parecidos), **PARE** a coleta e pergunte ao usuário para esclarecer. Sua resposta final deve ser apenas a pergunta.
            -   **Todos os IDs Coletados:** Se você coletou com sucesso todos os IDs obrigatórios (responsável, produto, ponto de estoque, talhão, safra), prossiga para a próxima fase.

        4.  **Tratamento de Falhas (REGRA MAIS IMPORTANTE):**
            -   Se qualquer ferramenta de busca (como `buscar_pontos_de_estoque_disponiveis`, `buscar_produto_por_nome`, etc.) retornar uma lista vazia (`[]`), isso significa que o item que o usuário mencionou **NÃO FOI ENCONTRADO**.
            -   Neste caso, você **DEVE PARAR** o processo de coleta de IDs.
            -   Sua resposta final **DEVE SER** uma mensagem amigável para o usuário, informando exatamente o que não foi encontrado e pedindo para ele verificar ou fornecer um nome válido.
            -   Exemplo de resposta: "Não consegui encontrar o ponto de estoque chamado 'FAZENDA RIBEIRA'. Você poderia verificar se o nome está correto ou me informar um dos pontos de estoque disponíveis?"

        5.  **Fase Final (Salvar):**
            -   Use a ferramenta `salvar_registro_consumo` com todos os IDs que você coletou.
            -   Sua resposta final **DEVE** ser o JSON exato retornado por esta ferramenta. Não adicione nenhuma outra palavra.

        **NÃO** tente salvar o registro antes de ter todos os IDs obrigatórios.
        Responda sempre em português (Brasil)."""

        agente_com_ferramentas = self._servico_llm.criar_agente_com_ferramentas(prompt_template=prompt_orquestrador, ferramentas=self.ferramentas)
        entradas_agente = {
            "input": mensagem_usuario,
            "dados_iniciais": dados_iniciais.dict(),
            # "dados_iniciais": dados_iniciais.model_dump(),
            "historico": historico_conversa
        }
        resultado = agente_com_ferramentas.executar(entradas_agente)
        return resultado