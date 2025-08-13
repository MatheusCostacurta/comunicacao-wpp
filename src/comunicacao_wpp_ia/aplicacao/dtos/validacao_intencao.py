from pydantic import BaseModel, Field

class ValidacaoIntencao(BaseModel):
    """Modelo para a saída da verificação de intenção do usuário."""
    intencao_valida: bool = Field(description="Indica se a intenção do usuário é válida (apenas registrar um consumo).")
    justificativa: str = Field(description="Uma justificativa concisa sobre o porquê da intenção ser considerada inválida.")