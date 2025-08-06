# -*- coding: utf-8 -*-
import os
from typing import List, Optional

# Adicionando um print de verificação para garantir que estamos executando a versão correta.
print("--- EXECUTANDO VERSÃO FINAL CORRIGIDA DO CÓDIGO (v4) ---")

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.tools import format_to_tool_messages
from langchain.agents.output_parsers.tools import ToolsAgentOutputParser


# Carrega as variáveis de ambiente
load_dotenv()


# --- Parte 1: Simulação da sua Infraestrutura (Sua API) ---
class MockAPI:
    """
    Esta classe simula as chamadas para sua API interna.
    """
    def get_produtos_do_produtor(self, id_produtor: int) -> List[dict]:
        print(f"\n[API MOCK] Buscando todos os produtos para o produtor {id_produtor}...")
        return [
            {"id": 101, "nome": "Glifosato Pro", "descricao": "Herbicida de amplo espectro"},
            {"id": 102, "nome": "Adubo Super Simples", "descricao": "Fertilizante fosfatado"},
            {"id": 103, "nome": "Tordon XT", "descricao": "Herbicida para pastagem"},
            {"id": 104, "nome": "Óleo Mineral Assist", "descricao": "Adjuvante agrícola"},
        ]

    def get_talhoes_do_produtor(self, id_produtor: int) -> List[dict]:
        print(f"\n[API MOCK] Buscando todos os talhões para o produtor {id_produtor}...")
        return [
            {"id": 201, "nome": "Talhão Norte", "area_ha": 50},
            {"id": 202, "nome": "Campo da Sede", "area_ha": 25},
            {"id": 203, "nome": "Talhão da Estrada", "area_ha": 70},
        ]

    def get_maquinas_do_produtor(self, id_produtor: int) -> List[dict]:
        print(f"\n[API MOCK] Buscando todas as máquinas para o produtor {id_produtor}...")
        return [
            {"id": 301, "nome": "Trator John Deere 6110J", "tipo": "Trator"},
            {"id": 302, "nome": "Pulverizador Autopropelido Uniport 3030", "tipo": "Pulverizador"},
        ]


api_mock = MockAPI()
ID_PRODUTOR_EXEMPLO = 1

@tool
def buscar_produtos_disponiveis() -> List[dict]:
    """Use esta ferramenta para obter uma lista de TODOS os produtos agrícolas disponíveis para o produtor. A IA deve então usar esta lista para encontrar o ID do produto que o usuário mencionou."""
    return api_mock.get_produtos_do_produtor(id_produtor=ID_PRODUTOR_EXEMPLO)

@tool
def buscar_talhoes_disponiveis() -> List[dict]:
    """Use esta ferramenta para obter uma lista de TODOS os talhões (áreas ou campos) disponíveis na fazenda do produtor. A IA deve então usar esta lista para encontrar o ID do talhão que o usuário mencionou."""
    return api_mock.get_talhoes_do_produtor(id_produtor=ID_PRODUTOR_EXEMPLO)

@tool
def buscar_maquinas_disponiveis() -> List[dict]:
    """Use esta ferramenta para obter uma lista de TODAS as máquinas (imobilizados) disponíveis para o produtor. A IA deve então usar esta lista para encontrar o ID da máquina que o usuário mencionou."""
    return api_mock.get_maquinas_do_produtor(id_produtor=ID_PRODUTOR_EXEMPLO)


class ConsumoInput(BaseModel):
    produto_mencionado: Optional[str] = Field(description="O nome do produto ou insumo mencionado na mensagem.")
    quantidade: Optional[str] = Field(description="A quantidade e a unidade de medida do consumo (ex: '20 kg', '15 litros').")
    talhao_mencionado: Optional[str] = Field(description="O nome do local, campo ou talhão onde o insumo foi aplicado.")
    maquina_mencionada: Optional[str] = Field(description="O nome da máquina ou trator utilizado na operação.")


def checar_informacoes_faltantes(mensagem_usuario: str, campos_obrigatorios: List[str], llm) -> (str | ConsumoInput):
    print("--- ETAPA 1: Checando informações obrigatórias ---")
    structured_llm = llm.with_structured_output(ConsumoInput, include_raw=False)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente que extrai informações de uma mensagem. Extraia os seguintes campos do texto do usuário."),
        ("human", "{mensagem}")
    ])
    chain = prompt | structured_llm
    dados_extraidos = chain.invoke({"mensagem": mensagem_usuario})
    print(f"Dados extraídos na checagem inicial: {dados_extraidos}")
    campos_faltantes = []
    mapa_perguntas = {
        "produto_mencionado": "Qual foi o produto utilizado?",
        "quantidade": "Qual foi a quantidade consumida?",
        "talhao_mencionado": "Em qual talhão ou área foi feita a aplicação?",
        "maquina_mencionada": "Qual máquina foi utilizada na operação?",
    }
    for campo in campos_obrigatorios:
        if not getattr(dados_extraidos, campo):
            campos_faltantes.append(mapa_perguntas[campo])
    if campos_faltantes:
        return "Para registrar o consumo, preciso de mais algumas informações: " + " ".join(campos_faltantes)
    else:
        return dados_extraidos


def executar_agente_principal(mensagem_usuario: str, dados_iniciais: ConsumoInput, llm):
    print("\n--- ETAPA 2: Acionando o Agente Orquestrador para buscar IDs (Método Robusto) ---")

    tools = [
        buscar_produtos_disponiveis,
        buscar_talhoes_disponiveis,
        buscar_maquinas_disponiveis,
    ]

    llm_with_tools = llm.bind_tools(tools)

    # CORREÇÃO FINAL: Ajustando a instrução final no prompt do sistema.
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é um assistente especialista em registros agrícolas.
Sua tarefa é identificar os IDs corretos para os itens mencionados pelo usuário, usando as ferramentas disponíveis.
- Dados Iniciais Extraídos: {dados_iniciais}
- O usuário disse: {input}

Seu plano de ação é:
1. Use as ferramentas para buscar as listas de produtos, talhões e máquinas.
2. Analise as listas e encontre os IDs correspondentes aos itens nos dados iniciais.
3. Quando tiver todos os IDs, responda DIRETAMENTE com o objeto JSON final. Não invente ou chame outras ferramentas. Apenas forneça o JSON como sua resposta final."""),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = (
        {
            "input": lambda x: x["input"],
            "dados_iniciais": lambda x: x["dados_iniciais"],
            "agent_scratchpad": lambda x: format_to_tool_messages(x["intermediate_steps"]),
        }
        | prompt
        | llm_with_tools
        | ToolsAgentOutputParser()
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )
    
    resultado = agent_executor.invoke({
        "input": mensagem_usuario,
        "dados_iniciais": dados_iniciais.dict()
    })

    return resultado.get("output", "Não foi possível determinar a resposta final.")


def processar_mensagem(mensagem: str):
    print(f"\n--- INICIANDO PROCESSAMENTO PARA: '{mensagem}' ---")
    campos_obrigatorios = ["produto_mencionado", "quantidade", "talhao_mencionado"]
    llm = ChatGroq(model_name="llama3-70b-8192", temperature=0)
    resultado_checaem = checar_informacoes_faltantes(mensagem, campos_obrigatorios, llm)
    if isinstance(resultado_checaem, str):
        print("\n--- RESULTADO FINAL (FALTAM DADOS) ---")
        print(f"Resposta para o usuário: {resultado_checaem}")
        return
    if isinstance(resultado_checaem, ConsumoInput):
        resultado_final = executar_agente_principal(mensagem, resultado_checaem, llm)
        print("\n--- RESULTADO FINAL (OBJETO MONTADO) ---")
        print(resultado_final)


if __name__ == "__main__":
    mensagem_completa = "Boa tarde, pode registrar aí o consumo de 15 litros de tordon no talhão da estrada. Usei o pulverizador uniport."
    processar_mensagem(mensagem_completa)
    
    print("\n" + "="*50 + "\n")
    
    mensagem_incompleta = "gastei 20kg de adubo super simples"
    processar_mensagem(mensagem_incompleta)