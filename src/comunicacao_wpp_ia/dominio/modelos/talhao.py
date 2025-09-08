from pydantic import BaseModel, Field

class Talhao(BaseModel):
    """DTO para representar um talhão (área ou campo) da fazenda."""
    id: str = Field(..., description="O ID único do talhão.")
    nome: str = Field(..., description="O nome do talhão.")
    area_ha: float = Field(..., description="A área do talhão em hectares.")