from typing import Type, TypeVar, List, Any, Dict
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.tools import format_to_tool_messages
from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM
from src.comunicacao_wpp_ia.aplicacao.portas.agente_com_ferramentas import AgenteComFerramentas
from src.comunicacao_wpp_ia.aplicacao.portas.agente import Agente

from src.comunicacao_wpp_ia.infraestrutura.ferramentas_llm.langchain_ferramentas_adapter import AdaptadorLangChainFerramentas
from src.comunicacao_wpp_ia.aplicacao.servicos.llms.utilizar_ferramenta import UtilizarFerramenta
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.repositorios.agriwin_ferramentas import RepoAgriwinFerramentas
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.saida.clientes_api.agriwin_cliente import AgriwinCliente

T = TypeVar('T', bound=BaseModel)

class _ExecutorAgenteGroq(Agente[T]):
    def __init__(self, cadeia_langchain: Any):
        self._cadeia = cadeia_langchain

    def executar(self, entrada: Any) -> T:
        return self._cadeia.invoke(entrada)
    
class _ExecutorAgenteComFerramentasGroq(AgenteComFerramentas):
    def __init__(self, executor_langchain: AgentExecutor):
        self._executor = executor_langchain

    def executar(self, entradas: Dict[str, Any]) -> str:
        resultado = self._executor.invoke(entradas)
        return resultado.get("output", "Não foi possível determinar a resposta final do agente.")
    

class AdaptadorGroq(ServicoLLM):
    """
    Implementação concreta (Adaptador) da porta ServicoLLM para a API da Groq.
    """
    def __init__(self, modelo: str = "llama-3.3-70b-versatile", temperatura: float = 0):
        self._llm = ChatGroq(model_name=modelo, temperature=temperatura)
        agriwin_urls = ["https://demo.agriwin.com.br"]
        agriwin_cliente = AgriwinCliente(base_urls=agriwin_urls)
        repo_ferramentas = RepoAgriwinFerramentas(agriwin_cliente=agriwin_cliente)
        servico_ferramentas = UtilizarFerramenta(
            repositorio_ferramentas=repo_ferramentas,
            id_produtor="NTc="
        )
        self.ferramentas_adapter = AdaptadorLangChainFerramentas(servico_ferramentas)
        print("[INFRA] Adaptador Groq inicializado.")

    def criar_agente(self, prompt_sistema: str, prompt_usuario: str, modelo_saida: Type[T]) -> T:
        llm_estruturado = self._llm.with_structured_output(modelo_saida, include_raw=False)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_sistema),
            ("human", prompt_usuario)
        ])
        
        chain = prompt | llm_estruturado
    
        return _ExecutorAgenteGroq(chain) 
    
    def criar_agente_com_ferramentas(self, prompt_template: str, ferramentas: List[Any]) -> AgenteComFerramentas:
        """
        Implementa o método fábrica para construir um agente com LangChain.
        """
        print("[ADAPTADOR GROQ] Criando uma instância de agente executável...")

        llm_com_ferramentas = self._llm.bind_tools(ferramentas)

        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_template),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        cadeia_agente = (
            {
                # Mapeia as chaves do dicionário de entrada para as variáveis do prompt
                "input": lambda x: x.get("input", ""),
                "dados_iniciais": lambda x: x.get("dados_iniciais", {}),
                "historico": lambda x: x.get("historico", []),
                "agent_scratchpad": lambda x: format_to_tool_messages(x.get("intermediate_steps", [])),
            }
            | prompt
            | llm_com_ferramentas
            | ToolsAgentOutputParser()
        )

        executor_langchain = AgentExecutor(
            agent=cadeia_agente,
            tools=ferramentas,
            verbose=True
        )

        # Retorna a nossa classe "wrapper" que implementa a porta Agente
        return _ExecutorAgenteComFerramentasGroq(executor_langchain)
    
    def obter_ferramentas(self) -> List[Any]:
        """
        Retorna a lista de ferramentas disponíveis para o agente.
        """
        return self.ferramentas_adapter.obter_ferramentas()