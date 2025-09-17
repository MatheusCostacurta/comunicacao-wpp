from pydantic import BaseModel, Field
from typing import Optional, List

class Produto(BaseModel):
    """Define a estrutura para um único produto a ser salvo."""
    id: str = Field(..., description="O ID do produto.")
    quantidade: float = Field(..., description="A quantidade consumida.")

class Maquina(BaseModel):
    """Define a estrutura para uma única máquina utilizada no consumo."""
    id: str = Field(..., description="O ID da máquina/imobilizado.")
    horimetro_inicio: Optional[float] = Field(None, description="O valor inicial do horímetro/odômetro.")
    horimetro_fim: Optional[float] = Field(None, description="O valor final do horímetro/odômetro.")

class Consumo(BaseModel):
    """
    DTO que representa o objeto de consumo após a fase de coleta de IDs, pronto para ser verificado e salvo.
    """
    produtos: List[Produto]
    id_ponto_estoque: Optional[str] = None
    id_safra: Optional[str] = None
    id_atividade: Optional[str] = None
    data_aplicacao: Optional[str] = None
    tipo_rateio: Optional[str] = None
    ids_plantios: Optional[List[str]] = None
    ids_propriedades: Optional[List[str]] = None
    id_responsavel: Optional[str] = None
    maquinas: Optional[List[Maquina]] = None
    epoca: Optional[str] = None
    observacao: Optional[str] = None