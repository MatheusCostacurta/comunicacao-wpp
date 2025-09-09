import os
import requests
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

from src.comunicacao_wpp_ia.aplicacao.portas.whatsapp import Whatsapp
from src.comunicacao_wpp_ia.aplicacao.dtos.mensagem_recebida import MensagemRecebida, TipoMensagem

# DTO específico para validar o payload do webhook da Z-API
class _ZAPIPayload(BaseModel):
    phone: str
    message_type: str = Field(..., alias="type")
    text: Optional[str] = None
    media_url: Optional[str] = Field(None, alias="mediaUrl")
    mime_type: Optional[str] = Field(None, alias="mimeType")

class AdaptadorZAPI(Whatsapp):
    """
    Implementação concreta (Adaptador) da porta ServicoMensageria para a Z-API.
    """
    def __init__(self):
        self.api_url = os.getenv("ZAPI_URL")
        if not self.api_url:
            raise ValueError("A variável de ambiente 'ZAPI_URL' não foi configurada.")
        
        self.headers = { "Content-Type": "application/json" }
        print("[INFRA] Adaptador Z-API inicializado.")

    def _baixar_midia(self, url: str) -> bytes:
        """Lógica de download, agora centralizada no adaptador."""
        print(f"[Z-API] Baixando mídia de {url}...")
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    
    def enviar(self, telefone: str, mensagem: str) -> None:
        """
        Envia uma mensagem de texto usando o endpoint /send-text da Z-API.
        """
        endpoint = f"{self.api_url}/send-text"
        payload = {
            "phone": telefone,
            "message": mensagem
        }
        try:
            print(f"[Z-API] Enviando mensagem para {telefone}...")
            print(f"[Z-API] Mensagem: {mensagem}")
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status() # Lança um erro para respostas HTTP 4xx/5xx
            print(f"[Z-API] Mensagem enviada com sucesso.")
        except requests.exceptions.RequestException as e:
            print(f"[Z-API ERROR] Falha ao enviar mensagem para {telefone}: {e}")

    def receber(self, payload_webhook: Dict[str, Any]) -> MensagemRecebida:
        try:
            payload = _ZAPIPayload.model_validate(payload_webhook)

            if payload.message_type == "chat" and payload.text:
                return MensagemRecebida(
                    telefone_remetente=payload.phone,
                    tipo="TEXTO",
                    texto_conteudo=payload.text
                )
            
            elif payload.message_type in ["image", "audio", "ptt"] and payload.media_url and payload.mime_type:
                conteudo_bytes = self._baixar_midia(payload.media_url)
                
                tipo_msg: TipoMensagem = "DESCONHECIDO"
                if "image" in payload.mime_type:
                    tipo_msg = "IMAGEM"
                elif "audio" in payload.mime_type:
                    tipo_msg = "AUDIO"

                return MensagemRecebida(
                    telefone_remetente=payload.phone,
                    tipo=tipo_msg,
                    media_conteudo=conteudo_bytes,
                    media_mime_type=payload.mime_type
                )
            
            raise ValueError(f"Tipo de mensagem não suportado ou payload incompleto: '{payload.message_type}'")

        except (ValidationError, requests.RequestException) as e:
            print(f"[Z-API ERROR] Falha ao processar webhook: {e}")
            raise ValueError("Payload do webhook inválido ou falha ao baixar mídia.")