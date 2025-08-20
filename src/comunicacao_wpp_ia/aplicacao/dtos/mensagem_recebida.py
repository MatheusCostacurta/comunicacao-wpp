from pydantic import BaseModel, Field
from typing import Optional, Literal

TipoMensagem = Literal["TEXTO", "AUDIO", "IMAGEM", "DESCONHECIDO"]

class MensagemRecebida(BaseModel):
    """
    DTO genérico e agnóstico para representar qualquer mensagem recebida.
    Ele lida com o conteúdo bruto (seja texto ou bytes de mídia).
    """
    telefone_remetente: str
    
    # Tipo da mensagem para roteamento na camada de aplicação
    tipo: TipoMensagem = Field(..., description="O tipo de conteúdo da mensagem.")
    
    # O conteúdo pode ser texto ou binário
    texto_conteudo: Optional[str] = None
    media_conteudo: Optional[bytes] = None
    media_mime_type: Optional[str] = None