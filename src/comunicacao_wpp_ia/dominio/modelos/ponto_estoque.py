from pydantic import BaseModel, Field

class PontoEstoque(BaseModel):
    """Modelo de domínio puro para um ponto de estoque."""
    id: str 
    nome: str
    ativo: bool