from pydantic import BaseModel, Field
from typing import Optional, List

class ProdutoParaSalvar(BaseModel):
    """Define a estrutura para um único produto a ser salvo."""
    id: int = Field(..., description="O ID do produto.")
    quantidade: float = Field(..., description="A quantidade consumida.")

class MaquinaParaSalvar(BaseModel):
    """Define a estrutura para uma única máquina utilizada no consumo."""
    id: int = Field(..., description="O ID da máquina/imobilizado.")
    horimetro_inicio: Optional[float] = Field(None, description="O valor inicial do horímetro/odômetro.")
    horimetro_fim: Optional[float] = Field(None, description="O valor final do horímetro/odômetro.")

# TODO: Nao seria modelo de dados, dominio?
class ConsumoMontado(BaseModel):
    """
    DTO que representa o objeto de consumo após a fase de coleta de IDs, pronto para ser verificado e salvo.
    """
    produtos: List[ProdutoParaSalvar]
    id_ponto_estoque: Optional[int] = None
    id_safra: Optional[int] = None
    data_aplicacao: Optional[str] = None
    tipo_rateio: Optional[str] = None
    ids_talhoes: Optional[List[int]] = None
    ids_propriedades: Optional[List[int]] = None
    id_responsavel: Optional[int] = None
    maquinas: Optional[List[MaquinaParaSalvar]] = None