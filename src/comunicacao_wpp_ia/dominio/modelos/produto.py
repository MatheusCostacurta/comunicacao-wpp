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
    DTO para representar um produto.
    """

    id: int = Field(..., alias='identificador')
    nome: str

    unidades_medida_raw: Optional[List[UnidadeMedida]] = Field(default=[], alias='unidades_medida')
    ingredientes_ativos_raw: Optional[List[IngredienteAtivo]] = Field(default=[], alias='ingredientes_ativo')

    # Campos que a aplicação realmente usará (listas de strings)
    # Eles serão populados pelo validador abaixo
    unidades_medida: List[str] = []
    ingredientes_ativos: List[str] = []

    # Validador que executa após a criação do modelo para transformar os dados
    @field_validator('unidades_medida_raw', 'ingredientes_ativos_raw', mode='after')
    def transformar_listas(cls, v, info):
        """
        Este método é chamado após a validação dos campos brutos.
        Ele extrai os textos dos objetos aninhados e popula os campos de listas de strings.
        """
        
        if not v:
            return v
        
        if info.field_name == 'unidades_medida_raw':
            info.data['unidades_medida'] = [um.sigla for um in v]
        
        if info.field_name == 'ingredientes_ativos_raw':
            info.data['ingredientes_ativos'] = [ia.nome for ia in v]
        
        return v