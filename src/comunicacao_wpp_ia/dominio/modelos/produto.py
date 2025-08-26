from pydantic import BaseModel, Field
from typing import List, Optional

class Produto(BaseModel):
    """DTO para representar um produto retornado pela API."""
    id: int = Field(..., description="O ID único do produto.")
    nome: str = Field(..., description="O nome do produto.")
    descricao: str = Field(..., description="A descrição do produto.")
    unidades_medida: Optional[List[str]] = Field(default=None, description="Lista de unidades de medida aceitas para o produto (ex: 'Litros', 'Kg').")
    ingredientes_ativos: Optional[List[str]] = Field(default=None, description="Lista de ingredientes ativos que compõem o produto.")