import os
from src.comunicacao_wpp_ia.aplicacao.portas.extrair_imagem import ServicoImagem
# Em um projeto real: from google.cloud import aiplatform as vertexai
from unittest.mock import MagicMock

# --- Simulação da API do Google Cloud Vertex AI (Gemini) ---
class MockVertexAI:
    def init(self, project: str, location: str):
        pass
    def GenerativeModel(self, model_name: str) -> MagicMock:
        def mock_generate_content(contents) -> MagicMock:
            response = MagicMock()
            response.text = "Registro de consumo: Produto: Tordon XT, Quantidade: 15 litros, Local: Talhão da Estrada, Equipamento: Pulverizador Uniport."
            return response
        model_mock = MagicMock()
        model_mock.generate_content.side_effect = mock_generate_content
        return model_mock
vertexai = MockVertexAI()
# --- Fim da simulação ---


class AdaptadorGeminiVision(ServicoImagem):
    """
    Implementação concreta (Adaptador) da porta ServicoImagem usando a API do Google Gemini.
    """
    def __init__(self):
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "seu-projeto-gcp")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        vertexai.init(project=project_id, location=location)
        self.model = vertexai.GenerativeModel("gemini-1.0-pro-vision")
        print("[INFRA] Adaptador Gemini Vision inicializado.")

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
            """
            conteudo_para_analise = [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
            print(f"Enviando {len(image_bytes)} bytes de imagem para análise...")
            response = self.model.generate_content(conteudo_para_analise)
            return response.text
        except Exception as e:
            print(f"Ocorreu um erro ao chamar a API de Visão: {e}")
            return ""