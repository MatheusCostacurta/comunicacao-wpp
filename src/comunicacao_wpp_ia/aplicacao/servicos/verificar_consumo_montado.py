from typing import Tuple
from pydantic import BaseModel, Field
from src.comunicacao_wpp_ia.aplicacao.dtos.consumo_para_salvar import ConsumoMontado
from src.comunicacao_wpp_ia.aplicacao.portas.llms import ServicoLLM

# TODO: Preciso de um agente para isso?
class ResultadoVerificacao(BaseModel):
    """Modelo de saída para o agente verificador."""
    aprovado: bool = Field(description="Indica se o consumo está aprovado para ser salvo.")
    justificativa: str = Field(description="Uma mensagem clara explicando o motivo da aprovação ou reprovação.")

def verificar_dados_consumo(consumo: ConsumoMontado, llm: ServicoLLM) -> ResultadoVerificacao:
    """
    Utiliza um agente LLM para verificar se o objeto de consumo montado está completo e lógico.
    Retorna um objeto ResultadoVerificacao.
    """
    print("\n--- ETAPA 3: Verificando os dados coletados com um Agente Verificador ---")

    prompt_sistema = """
    Você é um auditor de dados rigoroso e atencioso. Sua tarefa é analisar o objeto JSON de um consumo agrícola e verificar se ele está pronto para ser salvo, de acordo com as seguintes regras:

    **Regras Obrigatórias:**
    1.  O campo 'produtos' não pode ser uma lista vazia. Cada item dentro de 'produtos' deve ter um 'id' e uma 'quantidade'.
    2.  Os campos 'id_ponto_estoque', 'id_safra' e 'data_aplicacao' não podem ser nulos.
    3.  O campo 'tipo_rateio' não pode ser nulo.
    4.  Se 'tipo_rateio' for 'talhao', a lista 'ids_talhoes' não pode ser vazia.
    5.  Se 'tipo_rateio' for 'propriedade', a lista 'ids_propriedades' não pode ser vazia.

    **Análise e Resposta:**
    - Se TODAS as regras forem atendidas, retorne `aprovado: true` e uma justificativa simples como "Dados consistentes e prontos para salvar."
    - Se QUALQUER regra for violada, retorne `aprovado: false` e uma `justificativa` amigável para o usuário, explicando exatamente o que está faltando. Por exemplo: "Notei que você não informou de qual estoque o produto saiu. Poderia me dizer, por favor?".
    """
    prompt_usuario = f"Por favor, analise este objeto de consumo: {consumo.model_dump_json(indent=2)}"

    # Criamos um agente específico para esta tarefa de verificação.
    agente_verificador = llm.criar_agente(
        prompt_sistema=prompt_sistema,
        prompt_usuario=prompt_usuario,
        modelo_saida=ResultadoVerificacao
    )

    resultado = agente_verificador.executar({}) # A entrada já está no prompt
    print(f"[VERIFICADOR] Resultado: Aprovado={resultado.aprovado}, Justificativa='{resultado.justificativa}'")
    return resultado