from pydantic import BaseModel, Field
from typing import Optional

class Imobilizado(BaseModel):
    """DTO para representar uma máquina ou imobilizado da fazenda."""
    id: int = Field(..., description="O ID único da máquina.")
    nome: str = Field(..., description="O nome ou descrição da máquina.")
    numero_serie: Optional[str] = Field(default=None, description="O número de série único da máquina.")
    horimetro_inicio: Optional[float] = Field(default=None, description="O valor inicial do horímetro ou odômetro.")
    horimetro_fim: Optional[float] = Field(default=None, description="O valor final do horímetro ou odômetro.")