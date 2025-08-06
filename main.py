from dotenv import load_dotenv
from conversasao import processar_mensagem

def run():
    """
    Ponto de entrada principal da aplicação.
    Carrega variáveis de ambiente e inicia o processamento das mensagens.
    """
    print("--- INICIALIZANDO APLICAÇÃO DE COMUNICAÇÃO WPP ---")
    load_dotenv()

    # --- Testes ---
    mensagem_completa = "Boa tarde, pode registrar aí o consumo de 15 litros de tordon no talhão da estrada. Usei o pulverizador uniport."
    processar_mensagem(mensagem_completa)
    
    print("\n" + "="*50 + "\n")
    
    mensagem_incompleta = "gastei 20kg de adubo super simples"
    processar_mensagem(mensagem_incompleta)

if __name__ == "__main__":
    run()