from pydantic import BaseModel, Field

class Produto(BaseModel):
    """DTO para representar um produto retornado pela API."""
    id: int = Field(..., description="O ID único do produto.")
    nome: str = Field(..., description="O nome do produto.")
    descricao: str = Field(..., description="A descrição do produto.")