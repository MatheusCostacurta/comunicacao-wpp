from src.comunicacao_wpp_ia.aplicacao.portas.whatsapp import Whatsapp

class NotificarExpiracaoConversa:
    """
    Caso de uso responsável por notificar o usuário que sua conversa expirou por inatividade.
    """
    def __init__(self, whatsapp: Whatsapp):
        self._whatsapp = whatsapp

    def executar(self, telefone: str):
        """
        Envia a mensagem de notificação de conversa finalizada.
        """
        print(f"[APP SERVICE] Executando notificação de expiração de sessão para o telefone: {telefone}")
        self._whatsapp.enviar(telefone, "Conversa Finalizada")