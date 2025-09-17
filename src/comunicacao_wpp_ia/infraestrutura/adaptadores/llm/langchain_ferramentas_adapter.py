import json
from langchain.tools import tool
from functools import partial
from typing import List, Any, Optional
from src.comunicacao_wpp_ia.aplicacao.portas.ferramentas import Ferramentas
from src.comunicacao_wpp_ia.dominio.modelos.dados_remetente import DadosRemetente

class AdaptadorLangChainFerramentas:
    """
    Adaptador que expõe as funcionalidades do ServicoFerramentas no formato
    que a biblioteca LangChain espera.
    
    Este adaptador agora é responsável por criar ferramentas dinamicamente
    com o contexto do usuário (remetente) embutido.
    """
    def __init__(self, servico_ferramentas: Ferramentas):
        self._servico = servico_ferramentas

        # O decorador @tool precisa ser aplicado a funções que o LangChain possa inspecionar.
        # Definimos estas funções dentro do construtor para capturar a instância `_servico`
        # do nosso serviço de aplicação (closure).

    def obter_ferramentas_com_contexto(self, remetente: DadosRemetente) -> List[Any]:
        """
        Retorna a lista de ferramentas prontas para LangChain, com o contexto
        do remetente (id_produtor, base_url) já injetado via functools.partial.
        O LLM não verá esses parâmetros, mas eles serão usados na execução.
        """
        # Cria funções parciais, pré-preenchendo os parâmetros de contexto
        buscar_produto_com_contexto = partial(self._servico.buscar_produto_por_nome, 
                                            base_url=remetente.base_url, 
                                            id_produtor=remetente.produtor_id[0])
        
        buscar_talhoes_com_contexto = partial(self._servico.buscar_talhoes_disponiveis,
                                            base_url=remetente.base_url,
                                            id_produtor=remetente.produtor_id[0])
        
        buscar_plantios_com_contexto = partial(self._servico.buscar_plantios_disponiveis,
                                            base_url=remetente.base_url,
                                            id_produtor=remetente.produtor_id[0])
        
        buscar_propriedades_com_contexto = partial(self._servico.buscar_propriedades_disponiveis,
                                                base_url=remetente.base_url,
                                                id_produtor=remetente.produtor_id[0])
        
        buscar_maquinas_com_contexto = partial(self._servico.buscar_maquinas_disponiveis,
                                            base_url=remetente.base_url,
                                            id_produtor=remetente.produtor_id[0])
        
        buscar_pontos_estoque_com_contexto = partial(self._servico.buscar_pontos_de_estoque_disponiveis,
                                                    base_url=remetente.base_url,
                                                id_produtor=remetente.produtor_id[0])
        
        buscar_safra_com_contexto = partial(self._servico.buscar_safra_disponivel,
                                            base_url=remetente.base_url,
                                        id_produtor=remetente.produtor_id[0])
        
        buscar_responsavel_com_contexto = partial(self._servico.buscar_responsavel_por_telefone,
                                                base_url=remetente.base_url,
                                                id_produtor=remetente.produtor_id[0])

        @tool
        def buscar_produto_por_nome(nome_produto: str) -> str:
            """
            Use esta ferramenta para obter um map de produtos similares com base no produto que usuário mencionou.
            A menção do usuário pode ser o nome do produto (ex: 'Tordon') ou um ingrediente ativo (ex: 'Glifosato').
            Esse map é composto por 3 listas: 'produtos_similares', 'produtos_em_estoque' e 'produtos_mais_consumidos'.
            Cada produto no retorno conterá seu ID, nome, descrição, e também uma lista de 'unidades_medida' e 'ingredientes_ativos'.
            A IA deve usar esse map para encontrar o ID do produto que o usuário mencionou, priorizando produtos que já foram consumidos ou que possuem estoque para casos de desempate.
            Retorna um JSON string com listas de produtos similares, em estoque e mais consumidos.
            """
            if not nome_produto or not isinstance(nome_produto, str):
                return json.dumps({"produtos_similares": [], "produtos_em_estoque": [], "produtos_mais_usados": []})
            
            resultado = buscar_produto_com_contexto(nome_produto=nome_produto)
            return json.dumps(resultado)

        @tool
        def buscar_talhoes_disponiveis() -> str:
            """
            Use esta ferramenta para obter uma lista de TODOS os plantios disponíveis na fazenda do produtor.
            A IA deve então usar esta lista para encontrar o(s) ID(s) dos plantios que correspondem ao talhão que o usuário mencionou (pode ser mais de um).
            Retorna um JSON string com a lista de TODOS os plantios disponíveis.
            """
            resultados = buscar_talhoes_com_contexto()
            return json.dumps(resultados)
        
        @tool
        def buscar_plantios_disponiveis() -> str:
            """
            Use esta ferramenta para obter uma lista de TODOS os plantios disponíveis na fazenda do produtor. 
            A IA deve então usar esta lista para encontrar o(s) ID(s) do plantio(s) que o usuário mencionou (pode ser mais de um).
            Retorna um JSON string com a lista de TODOS os plantios disponíveis.
            """
            resultados = buscar_plantios_com_contexto()
            return json.dumps(resultados)

        @tool
        def buscar_propriedades_disponiveis() -> str:
            """
            Use esta ferramenta para obter uma lista de TODAS as propriedades (fazendas) disponíveis para o produtor.
            A IA deve usar esta lista para encontrar o(s) ID(s) da(s) propriedade(s) que o usuário mencionou (pode ser mais de uma).
            Retorna um JSON string com a lista de TODAS as propriedades disponíveis.
            """
            resultados = buscar_propriedades_com_contexto()
            return json.dumps(resultados)

        @tool
        def buscar_maquinas_disponiveis(nome_maquina: str) -> str:
            """
            Use esta ferramenta para encontrar uma ou mais máquinas (imobilizados) com base no que o usuário mencionou.
            O termo de busca pode ser o nome da máquina (ex: 'Trator John Deere') ou o seu número de série (ex: 'JD6110JBR').
            A ferramenta buscará por similaridade no nome (score 80) ou por correspondência exata no número de série.
            A IA deve então usar esta lista para encontrar o ID da máquina que o usuário mencionou

            Retorna um JSON string com a lista de máquinas encontradas.
            """
            if not nome_maquina or not isinstance(nome_maquina, str):
                return json.dumps([])
            resultado = buscar_maquinas_com_contexto(nome_maquina=nome_maquina)
            return json.dumps(resultado)

        @tool
        def buscar_pontos_de_estoque_disponiveis(nome_ponto_estoque: Optional[str] = None) -> str:
            """
            Use esta ferramenta para encontrar o ID do ponto de estoque (depósito) que o usuário mencionou. Forneça o nome mencionado para encontrar o melhor candidato.
            - Se o usuário mencionou um nome (ex: 'depósito da sede'), passe a string para o parâmetro 'nome_ponto_estoque'. A ferramenta retornará uma lista de pontos de estoque com nome similar ou vazia.
            - Se o usuário NÃO mencionou um ponto de estoque, chame a ferramenta sem nenhum parâmetro (deixe como None).
            """
            resultado = buscar_pontos_estoque_com_contexto(nome_ponto_estoque=nome_ponto_estoque)
            return json.dumps(resultado)

        @tool
        def buscar_safra_disponivel(nome_safra: Optional[str] = None) -> str:
            """
            Use esta ferramenta para encontrar a safra. 
            - Se o usuário mencionou um período (ex: 'safra 24/25', '2023/2024'), passe a string para o parâmetro 'nome_safra'.
            - Se o usuário NÃO mencionou um período de safra, chame a ferramenta sem nenhum parâmetro para obter a safra atual com base na data de hoje.

            Retorna um JSON string com a safra encontrada (pelo nome ou a safra ativa).
            """
            resultado = buscar_safra_com_contexto(nome_safra=nome_safra)
            return resultado

        @tool
        def buscar_responsavel_por_telefone(telefone: str) -> str:
            """
            Use esta ferramenta para encontrar o ID do responsável com base no número de telefone do remetente.
            Retorna um JSON string com o responsável encontrado pelo telefone.
            """
            if not telefone or not isinstance(telefone, str):
                return json.dumps(None)
            resultado = buscar_responsavel_com_contexto(telefone=telefone)
            return json.dumps(resultado)

        ferramentas: List[Any] = [
            buscar_produto_por_nome,
            buscar_talhoes_disponiveis,
            buscar_plantios_disponiveis,
            buscar_propriedades_disponiveis,
            buscar_maquinas_disponiveis,
            buscar_pontos_de_estoque_disponiveis,
            buscar_safra_disponivel,
            buscar_responsavel_por_telefone
        ]

        return ferramentas

# def obter_ferramentas(self) -> List[Any]:
#     """
#     Retorna a lista de ferramentas adaptadas e prontas para serem usadas
#     pelo agente LangChain.
#     """
#     return self.ferramentas