from pydantic import BaseModel
from typing import List, Optional

class DadosRemetente(BaseModel):
    """DTO para representar os dados do remetente da mensagem."""
    produtor_id: Optional[List[str]] = []
    numero_telefone: str 
    base_url: str