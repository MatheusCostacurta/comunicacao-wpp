from abc import ABC, abstractmethod
from typing import TypeVar, Any, Generic
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class Agente(Generic[T], ABC):
    """
    Define a interface (Porta) para um objeto que pode ser invocado ara produzir uma saída estruturada (Pydantic).
    """
    @abstractmethod
    def executar(self, entrada: Any) -> T:
        """
        Executa o agente com uma entrada e retorna o objeto Pydantic.
        """
        pass