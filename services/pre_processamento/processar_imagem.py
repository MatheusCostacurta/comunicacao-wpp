import os
from typing import Dict
# Em um projeto real: pip install google-cloud-aiplatform
# Para este exemplo, vamos simular a biblioteca.
from unittest.mock import MagicMock

# --- Simulação da API do Google Cloud Vertex AI (Gemini) ---
# Esta parte simula a interação com o Gemini para análise de imagem.
class MockVertexAI:
    def init(self, project: str, location: str):
        print(f"[MOCK VertexAI] Inicializado para projeto '{project}' na localização '{location}'.")

    def GenerativeModel(self, model_name: str) -> MagicMock:
        print(f"[MOCK VertexAI] Carregando modelo multimodal: {model_name}")
        
        def mock_generate_content(contents) -> MagicMock:
            # Simula a análise da imagem e retorna o texto que o Gemini extrairia.
            response = MagicMock()
            response.text = "Registro de consumo: Produto: Tordon XT, Quantidade: 15 litros, Local: Talhão da Estrada, Equipamento: Pulverizador Uniport."
            print(f"[MOCK VertexAI] Imagem analisada. Texto extraído: '{response.text}'")
            return response
            
        model_mock = MagicMock()
        model_mock.generate_content.side_effect = mock_generate_content
        return model_mock

vertexai = MockVertexAI()
# --- Fim da simulação ---


def inicializar_cliente_visao():
    """Inicializa e retorna o cliente do modelo de visão."""
    # Em um projeto real, a autenticação seria gerenciada via variáveis de ambiente
    # ou configuração do gcloud.
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "seu-projeto-gcp")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    vertexai.init(project=project_id, location=location)
    
    # Usamos o Gemini 1.0 Pro Vision, que é excelente para tarefas multimodais.
    # Em implementações mais recentes, poderia ser o Gemini 1.5.
    model = vertexai.GenerativeModel("gemini-1.0-pro-vision")
    return model

# Instância única do cliente
vision_model = inicializar_cliente_visao()

def extrair_texto_de_imagem(image_bytes: bytes) -> str:
    """
    Usa um modelo de IA multimodal (Gemini Vision) para extrair informações
    de consumo agrícola a partir dos bytes de uma imagem.

    Args:
        image_bytes: Os bytes brutos da imagem (PNG, JPEG, etc.).

    Returns:
        Uma string de texto com as informações extraídas, ou uma string vazia em caso de erro.
    """
    print("\n--- ETAPA DE INTERPRETAÇÃO DE IMAGEM (GEMINI) ---")
    if not image_bytes:
        print("Erro: Nenhum byte de imagem foi fornecido.")
        return ""

    try:
        # Prompt para o modelo: dizemos a ele exatamente o que procurar.
        prompt = """
        Analise a imagem a seguir, que pode ser uma nota fiscal, um rótulo de produto ou uma anotação manuscrita.
        Sua tarefa é identificar e extrair as seguintes informações sobre um consumo agrícola:
        - O nome do produto ou insumo.
        - A quantidade utilizada (com unidade de medida).
        - O local (talhão, campo, área) da aplicação.
        - (Opcional) A máquina ou equipamento utilizado.

        Retorne as informações em uma única frase de texto simples. Por exemplo:
        'Usei 15 litros de Tordon XT no Talhão da Estrada com o pulverizador.'
        """
        
        # A API espera uma lista de conteúdos (texto e imagem)
        conteudo_para_analise = [
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes} # Assumindo JPEG, mas a API suporta outros
        ]

        print(f"Enviando {len(image_bytes)} bytes de imagem para análise...")
        response = vision_model.generate_content(conteudo_para_analise)
        
        return response.text

    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API de Visão: {e}")
        return ""