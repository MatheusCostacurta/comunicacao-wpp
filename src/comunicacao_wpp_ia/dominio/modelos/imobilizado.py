from pydantic import BaseModel, Field

class Imobilizado(BaseModel):
    """DTO para representar uma máquina ou imobilizado da fazenda."""
    id: int = Field(..., description="O ID único da máquina.")
    nome: str = Field(..., description="O nome ou descrição da máquina.")
    tipo: str = Field(..., description="O tipo da máquina (ex: 'Trator', 'Pulverizador').")