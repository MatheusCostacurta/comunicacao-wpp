from pydantic import BaseModel, Field
from typing import Optional

class Imobilizado(BaseModel):
    """DTO para representar uma máquina ou imobilizado da fazenda."""
    id: int = Field(..., description="O ID único da máquina.", alias='identificador')
    nome: str = Field(..., description="O nome ou descrição da máquina.", alias='descricao')
    ativo: bool = Field(..., description="Indica se o imobilizado está ativo.")
    
    numero_serie: Optional[str] = Field(default=None, description="O número de série único da máquina.")
    horimetro_atual: Optional[str] = Field(default=None, description="O valor atual do horímetro ou odômetro.")