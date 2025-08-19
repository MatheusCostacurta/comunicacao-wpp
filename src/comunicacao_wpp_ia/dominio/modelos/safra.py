from pydantic import BaseModel, Field

class Safra(BaseModel):
    """DTO para representar uma safra agrícola."""
    id: int = Field(..., description="O ID único da safra.")
    nome: str = Field(..., description="O nome da safra (ex: 'Safra 23/24 Soja').")
    esta_ativa: bool = Field(..., description="Indica se é a safra corrente.")