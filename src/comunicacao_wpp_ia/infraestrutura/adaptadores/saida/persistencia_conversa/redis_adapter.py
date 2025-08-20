import redis
import json
import os
from typing import Dict, List, Any
from src.comunicacao_wpp_ia.aplicacao.portas.memorias import ServicoMemoriaConversa

# Tempo máximo em segundos para uma conversa inativa permanecer no Redis
TEMPO_MAXIMO_INATIVIDADE_SEGUNDOS = 1800  # 30 minutos

class AdaptadorRedis(ServicoMemoriaConversa):
    """
    Implementação concreta (Adaptador) da porta ServicoMemoria usando Redis como backend.
    """
    def __init__(self, db=0):
        """
        Inicializa o cliente Redis lendo a configuração das variáveis de ambiente.
        """
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', 6379))
        
        print("--- INICIALIZANDO ADAPTADOR DE MEMÓRIA COM REDIS ---")
        try:
            self._cliente_redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self._cliente_redis.ping()
            print(f"Conexão com o Redis estabelecida com sucesso em {host}:{port}.")
        except redis.exceptions.ConnectionError as e:
            print(f"ERRO CRÍTICO: Não foi possível conectar ao Redis em {host}:{port}.")
            raise

    def _gerar_chave(self, chave_identificadora: str) -> str:
        return f"conversa:{chave_identificadora}"

    def obter_estado(self, chave_identificadora: str) -> Dict[str, Any]:
        chave = self._gerar_chave(chave_identificadora)
        estado_salvo_json = self._cliente_redis.get(chave)
        if estado_salvo_json:
            print(f"[REDIS] Estado encontrado para '{chave_identificadora}'.")
            self._cliente_redis.expire(chave, TEMPO_MAXIMO_INATIVIDADE_SEGUNDOS)
            return json.loads(estado_salvo_json)
        else:
            print(f"[REDIS] Nenhum estado encontrado para '{chave_identificadora}'. Criando um novo.")
            return {"historico": []}

    def salvar_estado(self, chave_identificadora: str, historico: List[Any]):
        chave = self._gerar_chave(chave_identificadora)
        estado = {"historico": historico}
        estado_json = json.dumps(estado)
        self._cliente_redis.setex(chave, TEMPO_MAXIMO_INATIVIDADE_SEGUNDOS, estado_json)
        print(f"[REDIS] Estado salvo para '{chave_identificadora}' com expiração de {TEMPO_MAXIMO_INATIVIDADE_SEGUNDOS} segundos.")

    def limpar_memoria_conversa(self, chave_identificadora: str):
        chave = self._gerar_chave(chave_identificadora)
        self._cliente_redis.delete(chave)
        print(f"[REDIS] Memória da conversa com '{chave_identificadora}' limpa.")