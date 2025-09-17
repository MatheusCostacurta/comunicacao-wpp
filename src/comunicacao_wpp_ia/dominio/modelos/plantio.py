from pydantic import BaseModel, Field
from src.comunicacao_wpp_ia.dominio.modelos.talhao import Talhao
from src.comunicacao_wpp_ia.dominio.modelos.propriedade import Propriedade

class Plantio(BaseModel):
    """DTO para representar um plantio."""
    id: str
    nome: str
    talhao: Talhao
    propriedade: Propriedade