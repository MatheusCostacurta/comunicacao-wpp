from pydantic import BaseModel, Field
from typing import Optional, Any

class RespostaApi(BaseModel):
    """
    DTO para padronizar a resposta da API externa, garantindo um contrato claro
    entre a camada de infraestrutura e a de aplicação.
    """
    status: int = Field(..., description="O código de status HTTP da resposta.")
    mensagem: str = Field(..., description="A mensagem principal retornada pela API.")
    dados: Optional[Any] = Field(default=None, description="Os dados detalhados da resposta, que podem ser uma lista de erros ou um objeto de sucesso.")