from abc import ABC, abstractmethod

class ServicoTranscricao(ABC):
    """
    Define a interface (Porta) para um serviço de transcrição de áudio.
    """

    @abstractmethod
    def transcrever(self, audio_bytes: bytes) -> str:
        """
        Converte os bytes de um áudio em texto.
        """
        pass