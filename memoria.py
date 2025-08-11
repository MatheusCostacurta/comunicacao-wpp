import redis
import json
import os  # Importe o módulo 'os'
from typing import Dict, List, Any

# Tempo máximo em segundos para uma conversa inativa permanecer no Redis
TEMPO_MAXIMO_INATIVIDADE_SEGUNDOS = 1800  # 30 minutos

class GerenciadorMemoria:
    """
    Gerencia o estado da conversa para múltiplos usuários (números de telefone)
    usando o Redis para persistência.
    """
    def __init__(self, db=0): # Removemos host e port da assinatura
        """
        Inicializa o cliente Redis lendo a configuração das variáveis de ambiente.
        """
        # Dentro do Docker Compose, o host 'redis' aponta para o contêiner do Redis.
        # Usamos 'localhost' como padrão para permitir testes locais sem Docker.
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', 6379))
        
        print("--- INICIALIZANDO GERENCIADOR DE MEMÓRIA COM REDIS ---")
        try:
            self._cliente_redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self._cliente_redis.ping()
            print(f"Conexão com o Redis estabelecida com sucesso em {host}:{port}.")
        except redis.exceptions.ConnectionError as e:
            print(f"ERRO CRÍTICO: Não foi possível conectar ao Redis em {host}:{port}.")
            raise

    # ... (o resto da classe permanece igual)
    def _gerar_chave(self, numero_telefone: str) -> str:
        return f"conversa:{numero_telefone}"

    def obter_estado(self, numero_telefone: str) -> Dict[str, Any]:
        chave = self._gerar_chave(numero_telefone)
        estado_salvo_json = self._cliente_redis.get(chave)
        if estado_salvo_json:
            print(f"[REDIS] Estado encontrado para '{numero_telefone}'.")
            self._cliente_redis.expire(chave, TEMPO_MAXIMO_INATIVIDADE_SEGUNDOS)
            return json.loads(estado_salvo_json)
        else:
            print(f"[REDIS] Nenhum estado encontrado para '{numero_telefone}'. Criando um novo.")
            return {"historico": []}

    def salvar_estado(self, numero_telefone: str, historico: List[Any]):
        chave = self._gerar_chave(numero_telefone)
        estado = {"historico": historico}
        estado_json = json.dumps(estado)
        self._cliente_redis.setex(chave, TEMPO_MAXIMO_INATIVIDADE_SEGUNDOS, estado_json)
        print(f"[REDIS] Estado salvo para '{numero_telefone}' com expiração de {TEMPO_MAXIMO_INATIVIDADE_SEGUNDOS} segundos.")

    def limpar_memoria_conversa(self, numero_telefone: str):
        chave = self._gerar_chave(numero_telefone)
        self._cliente_redis.delete(chave)
        print(f"[REDIS] Memória da conversa com '{numero_telefone}' limpa.")