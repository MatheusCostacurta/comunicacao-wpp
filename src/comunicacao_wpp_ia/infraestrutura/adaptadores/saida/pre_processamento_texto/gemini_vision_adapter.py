import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.oauth2 import service_account
from src.comunicacao_wpp_ia.aplicacao.portas.extrair_imagem import ServicoImagem

def get_google_credentials():
    """
    Constrói o objeto de credenciais do Google a partir das variáveis de ambiente.
    """
    # Carrega as credenciais das variáveis de ambiente
    gcp_client_email = os.getenv("GCP_CLIENT_EMAIL")
    gcp_private_key = os.getenv("GCP_PRIVATE_KEY")

    if not gcp_client_email or not gcp_private_key:
        print("[INFRA WARNING] Credenciais GCP (GCP_CLIENT_EMAIL, GCP_PRIVATE_KEY) não encontradas nas variáveis de ambiente. Tentando autenticação padrão.")
        # Se as variáveis não estiverem definidas, o SDK tentará a autenticação padrão
        # (útil em ambientes como Google Cloud Run, etc.)
        return None

    # A chave privada precisa ter as quebras de linha restauradas
    gcp_private_key = gcp_private_key.replace('\\n', '\n')

    # Monta o dicionário de informações da credencial
    creds_info = {
        "type": "service_account",
        "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "private_key": gcp_private_key,
        "client_email": gcp_client_email,
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    
    # Cria o objeto de credenciais a partir do dicionário
    return service_account.Credentials.from_service_account_info(creds_info)


class AdaptadorGeminiVision(ServicoImagem):
    """
    Implementação concreta (Adaptador) da porta ServicoImagem usando a API do Google Gemini (Vertex AI).
    """
    def __init__(self):
        try:
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

            if not project_id:
                raise ValueError("A variável de ambiente 'GOOGLE_CLOUD_PROJECT' não foi configurada.")

            # Obtém as credenciais usando nossa nova função
            credentials = get_google_credentials()
            
            vertexai.init(project=project_id, location=location, credentials=credentials)
            
            self.model = GenerativeModel("gemini-2.5-pro")
            print("[INFRA] Adaptador Gemini Vision (Google Cloud) inicializado com sucesso.")
        except Exception as e:
            print(f"[INFRA ERROR] Falha ao inicializar o cliente Gemini Vision: {e}")
            raise

    def extrair_texto_de_imagem(self, image_bytes: bytes) -> str:
        print("\n--- ETAPA DE INTERPRETAÇÃO DE IMAGEM (GEMINI) ---")
        if not image_bytes:
            print("Erro: Nenhum byte de imagem foi fornecido.")
            return ""
            
        try:
            prompt = """
            Analise a imagem a seguir, que pode ser uma nota fiscal, um rótulo de produto ou uma anotação manuscrita.
            Sua tarefa é identificar e extrair as seguintes informações sobre um consumo agrícola:
            - O nome do produto ou insumo.
            - A quantidade utilizada (com unidade de medida).
            - O local (talhão, campo, área) da aplicação.
            - (Opcional) A máquina ou equipamento utilizado.
            Retorne as informações em uma única frase de texto simples.
            Se a imagem não contiver informações relevantes, retorne uma string vazia.
            """
            
            image_part = Part.from_data(
                mime_type="image/jpeg",
                data=image_bytes
            )

            print(f"Enviando {len(image_bytes)} bytes de imagem para análise no Gemini Vision...")
            response = self.model.generate_content([image_part, prompt])
            
            texto_extraido = response.text
            print(f"Texto extraído com sucesso: '{texto_extraido}'")
            return texto_extraido

        except Exception as e:
            print(f"Ocorreu um erro ao chamar a API do Gemini Vision: {e}")
            return ""