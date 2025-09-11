from abc import ABC, abstractmethod
from typing import Type, TypeVar, List, Any, Dict
from pydantic import BaseModel
from src.comunicacao_wpp_ia.aplicacao.portas.agente_com_ferramentas import AgenteComFerramentas
from src.comunicacao_wpp_ia.aplicacao.portas.agente import Agente
from src.comunicacao_wpp_ia.dominio.modelos.dados_remetente import DadosRemetente

T = TypeVar('T', bound=BaseModel)

class ServicoLLM(ABC):
    """
    Define a interface (Porta) para interagir com um modelo de linguagem.
    A camada de aplicação dependerá desta abstração, nunca de uma implementação concreta.
    """
    
    @abstractmethod
    def criar_agente(self, prompt_sistema: str, prompt_usuario: str, modelo_saida: Type[T]) -> Agente[T]:
        """
        Método Fábrica: constrói e retorna um Invocador para gerar saídas estruturadas.
        """
        pass

    @abstractmethod
    def criar_agente_com_ferramentas(self, remetente: DadosRemetente, prompt_template: str) -> AgenteComFerramentas:
        """
        Método Fábrica: constrói e retorna uma instância de um Agente executável.
        
        Args:
            prompt_template: O template de prompt do sistema para o agente.
            ferramentas: A lista de ferramentas que o agente pode usar.

        Returns:
            Um objeto que implementa a interface Agente.
        """
        pass