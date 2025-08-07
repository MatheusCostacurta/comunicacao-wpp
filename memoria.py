from datetime import datetime, timedelta
from typing import Dict, List, Any

# Tempo máximo de inatividade em minutos antes de limpar a memória da conversa
TEMPO_MAXIMO_INATIVIDADE_MINUTOS = 30

class GerenciadorMemoria:
    """
    Gerencia o estado da conversa para múltiplos usuários (números de telefone).
    Armazena o histórico e o tempo da última interação.
    """
    def __init__(self):
        self.conversas: Dict[str, Dict[str, Any]] = {}

    def _get_timestamp_atual(self) -> datetime:
        """Retorna o timestamp atual."""
        return datetime.now()

    def obter_estado(self, numero_telefone: str) -> Dict[str, Any]:
        """
        Recupera o estado da conversa para um número de telefone.
        Se não existir, cria um novo estado.
        """
        if numero_telefone not in self.conversas:
            self.conversas[numero_telefone] = {
                "historico": [],
                "ultimo_acesso": self._get_timestamp_atual()
            }
        return self.conversas[numero_telefone]

    def salvar_estado(self, numero_telefone: str, historico: List[Any]):
        """
        Salva o novo estado da conversa e atualiza o timestamp.
        """
        if numero_telefone in self.conversas:
            self.conversas[numero_telefone]["historico"] = historico
            self.conversas[numero_telefone]["ultimo_acesso"] = self._get_timestamp_atual()

    def limpar_conversas_inativas(self):
        """
        Verifica e remove conversas que estão inativas por mais tempo que o permitido.
        Este método pode ser chamado periodicamente por um processo em background.
        """
        print("\n--- EXECUTANDO LIMPEZA DE MEMÓRIA ---")
        agora = self._get_timestamp_atual()
        limite_tempo = timedelta(minutes=TEMPO_MAXIMO_INATIVIDADE_MINUTOS)
        
        numeros_para_remover = [
            numero
            for numero, dados in self.conversas.items()
            if agora - dados["ultimo_acesso"] > limite_tempo
        ]

        if not numeros_para_remover:
            print("Nenhuma conversa inativa para limpar.")
            return

        for numero in numeros_para_remover:
            del self.conversas[numero]
            print(f"Memória da conversa com '{numero}' limpa por inatividade.")