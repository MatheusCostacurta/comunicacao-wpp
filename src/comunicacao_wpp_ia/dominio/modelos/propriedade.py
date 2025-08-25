from pydantic import BaseModel, Field

class Propriedade(BaseModel):
    """DTO para representar uma propriedade (fazenda) da empresa."""
    id: int = Field(..., description="O ID único da propriedade.")
    nome: str = Field(..., description="O nome da propriedade.")