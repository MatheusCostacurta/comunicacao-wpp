import os
import redis
import threading
from src.comunicacao_wpp_ia.aplicacao.servicos.notificacoes.notificar_expiracao_conversa import NotificarExpiracaoConversa

class AdaptadorListenerRedis:
    """
    Adaptador Primário (Driving Adapter) que ouve por eventos de expiração
    de chaves no Redis e aciona o caso de uso de notificação na camada de aplicação.
    """
    def __init__(self, servico_notificacao: NotificarExpiracaoConversa):
        self._servico_notificacao = servico_notificacao
        self._thread = threading.Thread(target=self._run, daemon=True)
        print("[INFRA] Adaptador de Listener Redis inicializado.")

    def _run(self):
        """
        Este método roda na thread em segundo plano.
        """
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', 6379))
        r = redis.Redis(host=host, port=port, db=0, decode_responses=True)
        pubsub = r.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe('__keyevent@0__:expired')
        print("[BACKGROUND LISTENER] Ouvindo por expirações de chaves no Redis...")

        for message in pubsub.listen():
            key_expirada = message.get("data")
            if key_expirada and key_expirada.startswith("conversa:"):
                try:
                    # Extrai o número de telefone da chave (ex: "conversa:+5541999991118")
                    telefone = key_expirada.split(":", 1)[1]
                    # Aciona o caso de uso da camada de aplicação
                    self._servico_notificacao.executar(telefone)
                except Exception as e:
                    print(f"[BACKGROUND LISTENER ERROR] Falha ao processar expiração para a chave '{key_expirada}': {e}")

    def start(self):
        """
        Inicia a thread do ouvinte.
        """
        print("[BACKGROUND LISTENER] Iniciando a thread do ouvinte Redis.")
        self._thread.start()