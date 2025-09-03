from pydantic import BaseModel, Field
from typing import Optional

class Responsavel(BaseModel):
    """DTO para representar um funcionário ou responsável."""
    id: int = Field(..., description="O ID único do responsável.")
    nome: str = Field(..., description="O nome do responsável.")
    nome_fantasia: Optional[str] = Field(..., description="O nome fantasia do pj responsável.")
    telefone: Optional[str] = Field(..., description="O número de telefone do responsável.")