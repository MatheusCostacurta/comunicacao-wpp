from pydantic import BaseModel, Field
from typing import Optional

class Imobilizado(BaseModel):
    """Modelo de domínio puro para uma máquina ou imobilizado."""
    id: int
    nome: str
    ativo: bool
    numero_serie: Optional[str] = None
    horimetro_atual: Optional[str] = None