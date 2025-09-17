from pydantic import BaseModel, Field
from typing import Optional, List

"""
Este módulo contém os Data Transfer Objects (DTOs) que representam a estrutura
exata dos dados retornados pela API externa da Agriwin.

Eles servem como um "contrato" de dados na fronteira da camada de infraestrutura,
garantindo que qualquer dado vindo de fora seja validado antes de ser processado
pelo sistema.
"""

class RemetenteAgriwinDTO(BaseModel):
    identificador: str
    nome: str
    
class UnidadeMedidaDTO(BaseModel):
    sigla: str

class IngredienteAtivoDTO(BaseModel):
    nome: str

class ProdutoAgriwinDTO(BaseModel):
    identificador: str
    nome: str
    unidades_medida: Optional[List[UnidadeMedidaDTO]] = []
    ingredientes_ativo: Optional[List[IngredienteAtivoDTO]] = []

class _PropriedadePlantioDTO(BaseModel):
    identificador: str
    descricao: str

class _TalhaoPlantioDTO(BaseModel):
    identificador: str
    descricao: str
    propriedade: _PropriedadePlantioDTO

class _SafraPlantioDTO(BaseModel):
    identificador: str

class _CulturaPlantioDTO(BaseModel):
    identificador: str
    descricao: str

# --- DTO Principal para a resposta de /plantios ---
class AreasAgriwinDTO(BaseModel):
    identificador: str
    ativo: bool
    safra: _SafraPlantioDTO
    talhao: _TalhaoPlantioDTO
    cultura: _CulturaPlantioDTO

# --- DTO para Imobilizado (Máquina) ---
class MaquinaAgriwinDTO(BaseModel):
    identificador: str
    descricao: str
    ativo: Optional[bool] = None
    numero_serie: Optional[str] = None
    horimetro_atual: Optional[str] = None

# --- DTO para Ponto de Estoque ---
class PontoEstoqueAgriwinDTO(BaseModel):
    identificador: str
    descricao: str
    ativo: Optional[bool] = None

# --- DTO para Safra ---
class SafraAgriwinDTO(BaseModel):
    identificador: str
    ano_inicio: int
    ano_termino: int
    data_inicio: str  # A API retorna a data como string
    data_termino: str # A API retorna a data como string

# --- DTO para Responsavel ---
class ResponsavelAgriwinDTO(BaseModel):
    identificador: str
    nome: str
    nome_fantasia: Optional[str] = None
    telefone: Optional[str] = None

class _ConsumoRateioAgriwinDTO(BaseModel):
    atividade_id: Optional[str] = None
    safra_id: Optional[str] = None
    tipo: Optional[str] = None
    propriedades: Optional[List[str]] = []
    plantios: Optional[List[str]] = []
    culturas: Optional[List[str]] = []
    lotes: Optional[List[str]] = []

class _ConsumoItemAgriwinDTO(BaseModel):
    id: str
    quantidade: int

class _ConsumoImobilizadoAgriwinDTO(BaseModel):
    id: str
    quantidade_horimetro_hodometro: Optional[int] = None

class ConsumoAgriwinRequest(BaseModel):
    data: str
    responsavel_id: Optional[str] = None
    ponto_estoque_id: Optional[str] = None
    tipo_operacao_id: Optional[str] = None
    observacao: Optional[str] = None
    rateio: Optional[_ConsumoRateioAgriwinDTO] = None
    imobilizados: Optional[List[_ConsumoImobilizadoAgriwinDTO]] = None
    itens: List[_ConsumoItemAgriwinDTO]