from pydantic import BaseModel, Field
from datetime import date

class Safra(BaseModel):
    """DTO para representar uma safra agrícola."""
    id: int = Field(..., description="O ID único da safra.")
    nome: str = Field(..., description="O nome descritivo da safra (ex: 'Safra 2024/2025').")
    ano_inicio: int = Field(..., description="O ano de início da safra.")
    ano_termino: int = Field(..., description="O ano de término da safra.")
    data_inicio: date = Field(..., description="A data de início do período da safra.")
    data_termino: date = Field(..., description="A data de término do período da safra.")