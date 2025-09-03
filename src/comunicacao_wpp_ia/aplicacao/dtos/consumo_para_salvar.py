from pydantic import BaseModel, Field
from typing import Optional, List

class ProdutoParaSalvar(BaseModel):
    """Define a estrutura para um único produto a ser salvo."""
    id: int = Field(..., description="O ID do produto.")
    quantidade: float = Field(..., description="A quantidade consumida.")

class MaquinaParaSalvar(BaseModel):
    """Define a estrutura para uma única máquina utilizada no consumo."""
    id: int = Field(..., description="O ID da máquina/imobilizado.")
    horimetro_inicio: Optional[float] = Field(None, description="O valor inicial do horímetro/odômetro.")
    horimetro_fim: Optional[float] = Field(None, description="O valor final do horímetro/odômetro.")