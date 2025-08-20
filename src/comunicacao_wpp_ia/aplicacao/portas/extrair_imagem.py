from abc import ABC, abstractmethod

class ServicoImagem(ABC):
    """
    Define a interface (Porta) para um serviço de análise de imagem.
    """

    @abstractmethod
    def extrair_texto_de_imagem(self, image_bytes: bytes) -> str:
        """
        Extrai texto relevante de uma imagem.
        """
        pass