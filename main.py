from dotenv import load_dotenv
from src.comunicacao_wpp_ia.aplicacao.servicos.conversasao import processar_mensagem
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.persistencia.redis_adapter import AdaptadorRedis
from src.comunicacao_wpp_ia.infraestrutura.adaptadores.llm.groq_adapter import AdaptadorGroq

def run():
    """
    Ponto de entrada principal da aplicação.
    Carrega variáveis de ambiente e inicia o processamento das mensagens.
    """
    print("--- INICIALIZANDO APLICAÇÃO DE COMUNICAÇÃO WPP ---")
    load_dotenv()

    # Estes objetos serão compartilhados por todas as chamadas durante a execução da aplicação.
    llm = AdaptadorGroq()

    # Cria uma instância única do gerenciador de memória
    gerenciador_memoria = AdaptadorRedis()

    # --- Simulação de conversas ---
    # Usuário 2: Envia uma mensagem incompleta
    numero_usuario_2 = "+5511988882222"
    mensagem_incompleta_1 = "gastei 20kg de adubo super simples"
    processar_mensagem(mensagem_incompleta_1, numero_usuario_2, gerenciador_memoria, llm)

    print("\n" + "="*50 + "\n")

    # Usuário 1: Envia uma mensagem completa
    # numero_usuario_1 = "+5541999991111"
    # mensagem_completa = "Boa tarde, pode registrar aí o consumo de 15 litros de tordon no talhão da estrada. Usei o pulverizador uniport."
    # processar_mensagem(mensagem_completa, numero_usuario_1, gerenciador_memoria, llm)

    print("\n" + "="*50 + "\n")

    # Usuário 2: Completa a informação
    mensagem_incompleta_2 = "foi no campo da sede"
    processar_mensagem(mensagem_incompleta_2, numero_usuario_2, gerenciador_memoria, llm)

    print("\n" + "="*50 + "\n")
    
    # Simula a passagem do tempo para testar a limpeza de memória
    print("Aguardando para simular inatividade...")
    # No exemplo, para não esperar 30 minutos, vamos forçar a limpeza
    # Em um cenário real, a linha abaixo seria `time.sleep(1800)` ou um job agendado.
    gerenciador_memoria.limpar_conversas_inativas()


if __name__ == "__main__":
    run()