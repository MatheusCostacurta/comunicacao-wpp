from typing import Optional, Literal, List, Union
from pydantic import BaseModel, Field
from datetime import date

class ProdutoConsumo(BaseModel):
    """Representa um único produto e sua quantidade mencionados na mensagem."""
    nome: str = Field(..., description="O nome do produto ou insumo.")
    quantidade: str = Field(..., description="A quantidade e a unidade de medida (ex: '1', '13', '10,5').")

class MaquinaConsumo(BaseModel):
    """Representa uma única máquina e seu horímetro mencionados na mensagem."""
    nome: str = Field(..., description="O nome ou número de série da máquina.")
    horimetro_inicio: Optional[float] = Field(default=None, description="O valor inicial do horímetro.")
    horimetro_fim: Optional[float] = Field(default=None, description="O valor final do horímetro.")

class Consumo(BaseModel):
    """Modelo de dados para a extração inicial de informações da mensagem do usuário."""
    produtos_mencionados: Optional[List[ProdutoConsumo]] = Field(default=None, description="Uma lista de todos os produtos e suas respectivas quantidades mencionados.")
    
    talhoes_mencionados: Optional[List[str]] = Field(default=None, description="Uma lista com os nomes dos locais, campos ou talhões onde o insumo foi aplicado.")
    propriedades_mencionadas: Optional[List[str]] = Field(default=None, description="Uma lista com os nomes das propriedades ou fazendas onde o insumo foi aplicado.")
    tipo_rateio: Optional[Literal['talhao', 'propriedade']] = Field(default=None, description="Indica se o custo do consumo deve ser rateado por 'talhao' ou para a 'propriedade' inteira.")

    maquinas_mencionadas: Optional[List[MaquinaConsumo]] = Field(default=None, description="Uma lista de todas as máquinas e seus respectivos horímetros mencionados.")
    
    ponto_estoque_mencionado: Optional[str] = Field(default=None, description="O nome do ponto de estoque de onde os produtos saíram.")
    data_mencionada: Optional[Union[str, date]] = Field(default=None, description="A data da aplicação em texto (ex: 'ontem', 'dia 20', '20/07', 20 de julho).")
    safra_mencionada: Optional[str] = Field(default=None, description="O nome da safra para a qual o consumo deve ser alocado (ex: 'safra de soja').")
    id_responsavel: Optional[int] = Field(default=None, description="O ID do responsável pelo registro, identificado pelo número de telefone.")