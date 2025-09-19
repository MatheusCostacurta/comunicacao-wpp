from typing import Tuple
from pydantic import BaseModel, Field
from src.comunicacao_wpp_ia.dominio.objetos.consumo import Consumo
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM

# TODO: Preciso de um agente para isso?
class ResultadoVerificacao(BaseModel):
    """Modelo de saída para o agente verificador."""
    aprovado: bool = Field(description="Indica se o consumo está aprovado para ser salvo.")
    justificativa: str = Field(description="Uma mensagem clara explicando o motivo da aprovação ou reprovação.")

def verificar_dados_consumo(consumo: Consumo, llm: ServicoLLM) -> ResultadoVerificacao:
    """
    Utiliza um agente LLM para verificar se o objeto de consumo montado está completo e lógico.
    Retorna um objeto ResultadoVerificacao.
    """
    print("\n--- ETAPA 3: Verificando os dados coletados com um Agente Verificador ---")

    prompt_sistema = """
    Você é um assistente de validação de dados agrícolas, e sua principal habilidade é se comunicar de forma clara e amigável com o usuário final.
    Sua tarefa é analisar os dados de um consumo agrícola e, se encontrar algum problema, gerar uma **pergunta amigável** para o usuário, explicando o que falta, **sem usar jargões técnicos**.

    **Sua Resposta (o campo 'justificativa'):**
    - DEVE ser uma mensagem para uma pessoa leiga.
    - NUNCA use palavras como: 'id', 'id_ponto_estoque', 'ids_plantios', 'tipo_rateio', 'JSON', 'campo', 'lista', 'nulo', 'vazio'.
    - Fale de forma natural, como se estivesse conversando.
    - Agrupe os problemas em uma única mensagem coesa, se possível.
    
    **Regras Obrigatórias:**
    1.  O campo 'produtos' não pode ser uma lista vazia. Cada item dentro de 'produtos' deve ter um 'id' e uma 'quantidade' (nao pode nulas, vazias ou 0).
        - **Problema Técnico:** O campo 'produtos' é vazio ou possui algum id nulo.
        - **Sua Resposta:** "Não foi possível identificar o produto mencionado. Poderia revisar e me informar novamente?"
    2.  Os campos 'id_ponto_estoque', 'id_safra' e 'data_aplicacao' não podem ser nulos ou vazios.
    2.1  Exemplo do Ponto de Estoque/Depósito faltando:
        - **Problema Técnico:** O campo 'id_ponto_estoque' é nulo.
        - **Sua Resposta:** "Não foi possível identificar o estoque mencionado. Poderia revisar e me informar novamente?"
    3.  O campo 'tipo_rateio' não pode ser nulo ou vazio.
    3.1  Se 'tipo_rateio' for 'plantio', a lista 'ids_plantios' não pode ser nula ou vazia.
    3.2. Se 'tipo_rateio' for 'propriedade', a lista 'ids_propriedades' não pode ser nula ou vazia.
    3.3  Exemplo de local da aplicação faltando:
        - **Problema Técnico:** O 'tipo_rateio' é 'plantio', mas a lista 'ids_plantios' está vazia.
        - **Sua Resposta:** "Não foi possível identificar o plantio mencionado. Poderia revisar e me informar novamente?"

    **Contexto Importante:**
    Se um campo de ID obrigatório estiver faltando (nulo ou vazio), significa que o sistema tentou encontrar essa informação com base na mensagem do usuário, mas não obteve sucesso. A informação foi mencionada, mas não foi encontrada na base de dados.
    
    **Análise e Resposta:**
    - Se TODAS as regras forem atendidas, retorne `aprovado: true` e uma justificativa simples como "Dados consistentes e prontos para salvar."
    - Se houver qualquer problema, retorne `aprovado: false` e a `justificativa` com a mensagem amigável que você criou.
    - - Lembre-se: A justificativa **DEVE** informar que não foi possível *identificar* ou *encontrar* o dado e solicitar/perguntar esse dado novamente.
    """
    prompt_usuario = "Por favor, analise este objeto de consumo: {consumo_json}"

    agente_verificador = llm.criar_agente(
        prompt_sistema=prompt_sistema,
        prompt_usuario=prompt_usuario,
        modelo_saida=ResultadoVerificacao
    )
    print(f"[VERIFICADOR] Consumo={consumo.model_dump_json(indent=2)}")
    resultado = agente_verificador.executar({"consumo_json": consumo.model_dump_json(indent=2)})
    print(f"[VERIFICADOR] Resultado: Aprovado={resultado.aprovado}, Justificativa='{resultado.justificativa}'")
    return resultado