import os, re
import requests
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError

from src.comunicacao_wpp_ia.aplicacao.portas.whatsapp import Whatsapp
from src.comunicacao_wpp_ia.aplicacao.dtos.mensagem_recebida import MensagemRecebida, TipoMensagem
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.entrada.whatsapp.zapi_dtos import ZAPIPayload

class AdaptadorZAPI(Whatsapp):
    """
    Implementação concreta (Adaptador) da porta ServicoMensageria para a Z-API.
    """
    def __init__(self):
        self.url_base = os.getenv("ZAPI_URL_BASE")
        self.instancia_id = os.getenv("ZAPI_INSTANCIA_ID")
        self.instancia_token = os.getenv("ZAPI_INSTANCIA_TOKEN")
        self.token_cliente = os.getenv("ZAPI_CLIENTE_TOKEN")
        if not self.url_base:
            raise ValueError("A variável de ambiente 'ZAPI_URL_BASE' não foi configurada.")
        if not self.instancia_id:
            raise ValueError("A variável de ambiente 'ZAPI_INSTANCIA_ID' não foi configurada.")
        if not self.instancia_token:
            raise ValueError("A variável de ambiente 'ZAPI_INSTANCIA_TOKEN' não foi configurada.")
        if not self.token_cliente:
            raise ValueError("A variável de ambiente 'ZAPI_CLIENTE_TOKEN' não foi configurada.")
        
        self.headers = { 
            "Content-Type": "application/json", 
            "Client-Token": self.token_cliente
        }
        print("[INFRA] Adaptador Z-API inicializado.")

    def _baixar_midia(self, url: str) -> bytes:
        """Lógica de download, agora centralizada no adaptador."""
        print(f"[Z-API] Baixando mídia de {url}...")
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    
    def _formatar_numero_telefone(self, telefone: str) -> str:
        """
        Remove o código do país (55) e caracteres não numéricos do telefone.
        """
        numeros = re.sub(r'\D', '', telefone) # Remove tudo que não for dígito
        
        # Se o número começar com 55 e tiver o tamanho de um celular com DDD (11 dígitos) + 55, remove o 55
        if numeros.startswith('55'):
            numeros = numeros[2:]
        
        # 3. Verifica a necessidade de adicionar o nono dígito.
        # Um número de celular no Brasil com DDD tem 10 (formato antigo) ou 11 (formato novo) dígitos.
        if len(numeros) == 10:
            ddd = numeros[:2]
            numero_sem_9 = numeros[2:]
            return f"{ddd}9{numero_sem_9}"
        
        return numeros
    
    def enviar(self, telefone: str, mensagem: str) -> None:
        """
        Envia uma mensagem de texto usando o endpoint /send-text da Z-API.
        """
        endpoint = f"{self.url_base}/instances/{self.instancia_id}/token/{self.instancia_token}/send-text"
        payload = {
            # "phone": f"+55{telefone}",
            "phone": "5542998536683",
            "message": mensagem
        }
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status() # Lança um erro para respostas HTTP 4xx/5xx
            print(f"[Z-API] Mensagem enviada com sucesso.")
        except requests.exceptions.RequestException as e:
            print(f"[Z-API ERROR] Falha ao enviar mensagem para {telefone}: {e}")

    def receber(self, payload_webhook: Dict[str, Any]) -> MensagemRecebida:
        try:
            payload = ZAPIPayload.model_validate(payload_webhook)
            telefone_formatado = self._formatar_numero_telefone(payload.phone)

            if payload.text and payload.text.message:
                print("[Z-API] Texto recebido")
                return MensagemRecebida(
                    telefone_formatado=telefone_formatado,
                    telefone_remetente=payload.phone,
                    tipo="TEXTO",
                    texto_conteudo=payload.text.message
                )
            elif payload.audio and payload.audio.audioUrl:
                print("[Z-API] Áudio recebido")
                conteudo_bytes = self._baixar_midia(payload.audio.audioUrl)
                return MensagemRecebida(
                    telefone_formatado=telefone_formatado,
                    telefone_remetente=payload.phone,
                    tipo="AUDIO",
                    media_conteudo=conteudo_bytes,
                    media_mime_type=payload.audio.mimeType
                )
            elif payload.image and payload.image.imageUrl:
                print("[Z-API] Imagem recebida")
                conteudo_bytes = self._baixar_midia(payload.image.imageUrl)
                return MensagemRecebida(
                    telefone_formatado=telefone_formatado,
                    telefone_remetente=payload.phone,
                    tipo="IMAGEM",
                    media_conteudo=conteudo_bytes,
                    media_mime_type=payload.image.mimeType
                )
            
            raise ValueError(f"Tipo de mensagem não suportado ou payload incompleto: '{payload.message_type}'")

        except (ValidationError, requests.RequestException) as e:
            print(f"[Z-API ERROR] Falha ao processar webhook: {e}")
            raise ValueError("Payload do webhook inválido ou falha ao baixar mídia.")