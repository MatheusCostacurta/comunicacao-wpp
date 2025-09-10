from abc import ABC, abstractmethod

class ExtrairTextoDaImagem(ABC):
    """
    Define a interface (Porta) para um serviço de análise de imagem.
    """

    @abstractmethod
    def executar(self, image_bytes: bytes) -> str:
        """
        Extrai texto relevante de uma imagem.
        """
        pass