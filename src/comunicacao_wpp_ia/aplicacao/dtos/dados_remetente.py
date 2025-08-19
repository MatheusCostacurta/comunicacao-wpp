from pydantic import BaseModel, Field

class DadosRemetente(BaseModel):
    """DTO para representar os dados do remetente da mensagem."""
    produtor_id: int = Field(description="O ID do produtor associado ao remetente.")
    numero_telefone: str = Field(description="O número de telefone do remetente, usado para identificar o responsável.")