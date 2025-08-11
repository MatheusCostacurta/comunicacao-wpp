from typing import Optional
from pydantic import BaseModel, Field

class ConsumoInput(BaseModel):
    """Modelo de dados para a extração inicial de informações da mensagem do usuário."""
    produto_mencionado: Optional[str] = Field(description="O nome do produto ou insumo mencionado na mensagem.")
    quantidade: Optional[str] = Field(description="A quantidade e a unidade de medida do consumo (ex: '20 kg', '15 litros').")
    talhao_mencionado: Optional[str] = Field(description="O nome do local, campo ou talhão onde o insumo foi aplicado.")
    maquina_mencionada: Optional[str] = Field(description="O nome da máquina ou trator utilizado na operação.")