from pydantic import BaseModel
from typing import Optional

class DadosRemetente(BaseModel):
    """DTO para representar os dados do remetente da mensagem."""
    produtor_id: Optional[str] = None
    numero_telefone: str 