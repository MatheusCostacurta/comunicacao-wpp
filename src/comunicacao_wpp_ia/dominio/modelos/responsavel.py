from pydantic import BaseModel, Field

class Responsavel(BaseModel):
    """DTO para representar um funcionário ou responsável."""
    id: int = Field(..., description="O ID único do responsável.")
    nome: str = Field(..., description="O nome do responsável.")
    telefone: str = Field(..., description="O número de telefone do responsável.")