from datetime import datetime, timedelta
from typing import Dict, List, Any
from src.comunicacao_wpp_ia.aplicacao.portas.memorias import ServicoMemoriaConversa

class AdaptadorMemoriaLocal(ServicoMemoriaConversa):
    """
    Gerencia o estado da conversa para múltiplos usuários (números de telefone).
    Armazena o histórico e o tempo da última interação.
    """
    def __init__(self):
        self.conversas: Dict[str, Dict[str, Any]] = {}

    def _get_timestamp_atual(self) -> datetime:
        """Retorna o timestamp atual."""
        return datetime.now()

    def _gerar_chave(self, chave_identificadora: str) -> str:
        return f"conversa:{chave_identificadora}"

    def obter_estado(self, chave_identificadora: str) -> Dict[str, Any]:
        """
        Recupera o estado da conversa para um número de telefone.
        Se não existir, cria um novo estado.
        """
        if chave_identificadora not in self.conversas:
            self.conversas[chave_identificadora] = {
                "historico": [],
                "ultimo_acesso": self._get_timestamp_atual()
            }
        return self.conversas[chave_identificadora]

    def salvar_estado(self, chave_identificadora: str, historico: List[Any]):
        """
        Salva o novo estado da conversa e atualiza o timestamp.
        """
        if chave_identificadora in self.conversas:
            self.conversas[chave_identificadora]["historico"] = historico
            self.conversas[chave_identificadora]["ultimo_acesso"] = self._get_timestamp_atual()

    def limpar_memoria_conversa(self, chave_identificadora: str):
        self.salvar_estado(chave_identificadora, [])
        print(f"[LOCAL] Memória da conversa com '{chave_identificadora}' limpa.")