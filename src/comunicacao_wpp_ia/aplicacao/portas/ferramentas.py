from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class Ferramentas(ABC):
    """
    Define a interface (Porta) para as ferramentas que o agente LLM pode invocar.
    Esta abstração pertence à camada de aplicação, pois define as capacidades
    que o núcleo da aplicação expõe.
    """

    @abstractmethod
    def buscar_produto_por_nome(self, nome_produto: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def buscar_talhoes_disponiveis(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def buscar_propriedades_disponiveis(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def buscar_plantios_disponiveis(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def buscar_maquinas_disponiveis(self, nome_maquina: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def buscar_pontos_de_estoque_disponiveis(self, nome_ponto_estoque: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def buscar_safra_disponivel(self, nome_safra: Optional[str] = None) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def buscar_responsavel_por_telefone(self, telefone: str) -> Optional[Dict[str, Any]]:
        pass