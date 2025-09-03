from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

# Modelo para representar o objeto de unidade de medida aninhado
class UnidadeMedida(BaseModel):
    sigla: str

# Modelo para representar o objeto de ingrediente ativo aninhado
class IngredienteAtivo(BaseModel):
    nome: str

class Produto(BaseModel):
    """
    Representa um Produto dentro do núcleo da aplicação.
    """
    id: int
    nome: str
    unidades_medida: List[str] = []
    ingredientes_ativos: List[str] = []