import os
from openai import OpenAI
from typing import BytesIO

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcrever_audio_whisper(audio_bytes: bytes, idioma: str = "pt") -> str:
    """
    Recebe os bytes de um arquivo de áudio e utiliza a API do OpenAI Whisper
    para transcrevê-lo para texto.

    Args:
        audio_bytes: Os bytes brutos do arquivo de áudio.
        idioma: O idioma do áudio para ajudar o modelo na transcrição (padrão 'pt-br').

    Returns:
        O texto transcrito como uma string.
    """
    print("\n--- ETAPA DE TRANSCRIÇÃO DE ÁUDIO (WHISPER) ---")
    if not audio_bytes:
        print("Erro: Nenhum byte de áudio foi fornecido.")
        return ""

    # A API do Whisper espera um objeto "file-like", então usamos BytesIO
    # para tratar os bytes em memória como se fosse um arquivo.
    # O nome do arquivo ('audio.mp3') é necessário para a API identificar o formato.
    audio_file = BytesIO(audio_bytes)
    audio_file.name = 'audio.mp3' # ou o formato que você for usar (m4a, wav, etc.)

    try:
        print(f"Enviando {len(audio_bytes)} bytes para a API do Whisper...")
        
        # Chamada real à API de transcrição
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=idioma
        )
        
        texto_resultante = transcription.text
        print(f"Texto transcrito com sucesso: '{texto_resultante}'")
        return texto_resultante

    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API do Whisper: {e}")
        # Retorna uma string vazia para que o fluxo principal possa tratar o erro.
        return ""