from pydantic import BaseModel, Field

class PontoEstoque(BaseModel):
    """DTO para representar um ponto de estoque (depósito) da fazenda."""
    id: int = Field(..., description="O ID único do ponto de estoque.", alias='identificador')
    nome: str = Field(..., description="O nome ou descrição do ponto de estoque.", alias='descricao')
    ativo: bool = Field(..., description="Indica se o ponto de estoque está ativo.")