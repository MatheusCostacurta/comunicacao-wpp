from pydantic import BaseModel, Field
from typing import Optional, List

"""
Este módulo contém os Data Transfer Objects (DTOs) que representam a estrutura
exata dos dados retornados pela API externa da Agriwin.

Eles servem como um "contrato" de dados na fronteira da camada de infraestrutura,
garantindo que qualquer dado vindo de fora seja validado antes de ser processado
pelo sistema.
"""

# --- DTOs para Produto ---
class UnidadeMedidaDTO(BaseModel):
    sigla: str

class IngredienteAtivoDTO(BaseModel):
    nome: str

class ProdutoAgriwinDTO(BaseModel):
    identificador: int
    nome: str
    unidades_medida: Optional[List[UnidadeMedidaDTO]] = []
    ingredientes_ativo: Optional[List[IngredienteAtivoDTO]] = []

# --- DTO para Talhao ---
class TalhaoAgriwinDTO(BaseModel):
    identificador: int
    nome: str
    area_ha: Optional[float] = None

# --- DTO para Propriedade ---
class PropriedadeAgriwinDTO(BaseModel):
    identificador: int
    nome: str

# --- DTO para Imobilizado (Máquina) ---
class ImobilizadoAgriwinDTO(BaseModel):
    identificador: int
    descricao: str
    ativo: Optional[bool] = None
    numero_serie: Optional[str] = None
    horimetro_atual: Optional[str] = None

# --- DTO para Ponto de Estoque ---
class PontoEstoqueAgriwinDTO(BaseModel):
    identificador: int
    descricao: str
    ativo: Optional[bool] = None

# --- DTO para Safra ---
class SafraAgriwinDTO(BaseModel):
    identificador: int
    nome: str
    ano_inicio: int
    ano_termino: int
    data_inicio: str  # A API retorna a data como string
    data_termino: str # A API retorna a data como string

# --- DTO para Responsavel ---
class ResponsavelAgriwinDTO(BaseModel):
    identificador: int
    nome: str
    nome_fantasia: Optional[str] = None
    telefone: Optional[str] = None