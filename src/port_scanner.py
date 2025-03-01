import socket
import threading
import logging

# Função para configurar o logging
def configure_logging(log_level):
    logging.basicConfig(
        filename='port_scanner.log',
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

# Função para configurar os parâmetros
def get_user_config():
    print("Configurações:")
    
    # Tempo limite de conexão (em segundos)
    timeout = input("Digite o tempo limite de conexão (em segundos): ")
    try:
        timeout = int(timeout)
    except ValueError:
        print("[Erro] Entrada inválida. Usando o valor padrão de 1 segundo.")
        timeout = 1

    # Número máximo de threads
    max_threads = input("Digite o número máximo de threads (padrão 10): ")
    try:
        max_threads = int(max_threads)
    except ValueError:
        print("[Erro] Entrada inválida. Usando o valor padrão de 10.")
        max_threads = 10

    # Nível de logging
    log_level_input = input("Escolha o nível de log (1: INFO, 2: WARNING, 3: ERROR): ")
    if log_level_input == "1":
        log_level = logging.INFO
    elif log_level_input == "2":
        log_level = logging.WARNING
    elif log_level_input == "3":
        log_level = logging.ERROR
    else:
        print("[Erro] Nível inválido. Usando o padrão INFO.")
        log_level = logging.INFO

    # Configuração de logging
    configure_logging(log_level)
    
    return timeout, max_threads

def scan_port(target, port, timeout):
    """Tenta se conectar a uma porta do alvo para verificar se está aberta."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)  # Tempo limite de resposta configurado pelo usuário
        result = sock.connect_ex((target, port))  # Retorna 0 se a porta estiver aberta
        sock.close()
        return result == 0  # Retorna True se a porta estiver aberta
    except socket.gaierror:
        logging.error(f"Não foi possível resolver o alvo: {target}. Verifique o IP ou domínio.")
        return False
    except socket.error as e:
        logging.error(f"Erro ao tentar conectar à porta {port} do alvo {target}: {e}")
        return False

def scan_ports(target, ports, timeout, max_threads):
    """Escaneia múltiplas portas no alvo fornecido usando threads."""
    threads = []
    for port in ports:
        # Limita o número de threads
        if len(threads) >= max_threads:
            for thread in threads:
                thread.join()  # Aguarda as threads anteriores terminarem antes de iniciar novas
            threads = []  # Reseta a lista de threads

        thread = threading.Thread(target=check_port, args=(target, port, timeout))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

def check_port(target, port, timeout):
    """Verifica o estado de uma porta e imprime o resultado, além de registrar o log."""
    if scan_port(target, port, timeout):
        message = f"[+] Porta {port} aberta em {target} ✅"
        print(message)
        logging.info(message)
    else:
        message = f"[-] Porta {port} fechada em {target} ❌"
        print(message)
        logging.info(message)

if __name__ == "__main__":
    try:
        # Configurações do usuário
        timeout, max_threads = get_user_config()
        
        target = input("Digite o IP ou domínio para escanear: ")
        ports = input("Digite as portas que deseja verificar (separadas por vírgula): ")
        ports = [int(port.strip()) for port in ports.split(",")]

        logging.info(f"Escaneando {target} nas portas: {ports}")
        scan_ports(target, ports, timeout, max_threads)
    except ValueError:
        logging.error("[Erro] Entrada inválida. Certifique-se de fornecer números válidos para as portas.")
        print("[Erro] Entrada inválida. Certifique-se de fornecer números válidos para as portas.")
    except Exception as e:
        logging.error(f"[Erro] Ocorreu um erro inesperado: {e}")
        print(f"[Erro] Ocorreu um erro inesperado: {e}")
