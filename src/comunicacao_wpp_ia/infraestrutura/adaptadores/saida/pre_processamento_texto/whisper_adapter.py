import os
from openai import OpenAI
from io import BytesIO
from src.comunicacao_wpp_ia.aplicacao.portas.transcrever_audio import ServicoTranscricao

class AdaptadorWhisper(ServicoTranscricao):
    """
    Implementação concreta (Adaptador) da porta ServicoTranscricao usando a API do OpenAI Whisper.
    """
    def __init__(self):
        # A inicialização do cliente OpenAI pode ser mais robusta,
        # lendo a chave de variáveis de ambiente.
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("[INFRA] Adaptador Whisper inicializado.")

    def transcrever(self, audio_bytes: bytes, idioma: str = "pt") -> str:
        print("\n--- ETAPA DE TRANSCRIÇÃO DE ÁUDIO (WHISPER) ---")
        if not audio_bytes:
            print("Erro: Nenhum byte de áudio foi fornecido.")
            return ""

        audio_file = BytesIO(audio_bytes)
        audio_file.name = 'audio.mp3'

        try:
            print(f"Enviando {len(audio_bytes)} bytes para a API do Whisper...")
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=idioma
            )
            texto_resultante = transcription.text
            print(f"Texto transcrito com sucesso: '{texto_resultante}'")
            return texto_resultante

        except Exception as e:
            print(f"Ocorreu um erro ao chamar a API do Whisper: {e}")
            return ""