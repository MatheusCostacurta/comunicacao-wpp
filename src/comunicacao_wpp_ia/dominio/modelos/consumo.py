from typing import Optional, Literal, List
from pydantic import BaseModel, Field
from datetime import date

class Consumo(BaseModel):
    """Modelo de dados para a extração inicial de informações da mensagem do usuário."""
    produto_mencionado: Optional[str] = Field(default=None, description="O nome do produto ou insumo mencionado na mensagem.")
    quantidade: Optional[str] = Field(default=None, description="A quantidade e a unidade de medida do consumo (ex: '20 kg', '15 litros').")
    
    talhoes_mencionados: Optional[List[str]] = Field(default=None, description="Uma lista com os nomes dos locais, campos ou talhões onde o insumo foi aplicado.")
    propriedades_mencionadas: Optional[List[str]] = Field(default=None, description="Uma lista com os nomes das propriedades ou fazendas onde o insumo foi aplicado.")
    tipo_rateio: Optional[Literal['talhao', 'propriedade']] = Field(default=None, description="Indica se o custo do consumo deve ser rateado por 'talhao' ou para a 'propriedade' inteira, identificado por nós")

    maquina_mencionada: Optional[str] = Field(default=None, description="O nome da máquina ou trator utilizado na operação.")
    ponto_estoque_mencionado: Optional[str] = Field(default=None, description="O nome do ponto de estoque de onde o produto saiu.")
    data_mencionada: Optional[date] = Field(default=None, description="A data da aplicação. Se não mencionada, deve ser a data atual.")
    safra_mencionada: Optional[str] = Field(default=None, description="O nome da safra para a qual o consumo deve ser alocado (ex: 'safra de soja').")
    id_responsavel: Optional[int] = Field(default=None, description="O ID do responsável pelo registro, identificado pelo número de telefone.")