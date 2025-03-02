import socket
import ssl
import dns.resolver
import threading
import logging
from tqdm import tqdm
import csv

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

# Função para escanear uma porta
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

# Função para escanear múltiplas portas
def scan_ports_with_progress(target, ports, timeout, max_threads):
    """Escaneia múltiplas portas no alvo fornecido usando threads e barra de progresso."""
    threads = []
    results = {}
    for port in tqdm(ports, desc="Escaneando portas", unit="porta"):
        # Limita o número de threads
        if len(threads) >= max_threads:
            for thread in threads:
                thread.join()  # Aguarda as threads anteriores terminarem antes de iniciar novas
            threads = []  # Reseta a lista de threads

        thread = threading.Thread(target=check_port, args=(target, port, timeout, results))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

    # Após o escaneamento, exporta os resultados para CSV
    export_results_to_csv(results)

# Função para verificar o status de uma porta
def check_port(target, port, timeout, results):
    """Verifica o estado de uma porta e imprime o resultado, além de registrar o log."""
    if scan_port(target, port, timeout):
        message = f"[+] Porta {port} aberta em {target} ✅"
        results[port] = "Aberta"
        # Chama a função grab_banner para capturar o banner da porta aberta
        banner = grab_banner(target, port)
        print(f"Banner da Porta {port}: {banner}")
    else:
        message = f"[-] Porta {port} fechada em {target} ❌"
        results[port] = "Fechada"
    print(message)
    logging.info(message)

# Função para exportar os resultados para CSV
def export_results_to_csv(results):
    """Exporta os resultados para um arquivo CSV."""
    with open('scan_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Porta', 'Status'])  # Cabeçalho
        for port, status in results.items():
            writer.writerow([port, status])  # Escreve os resultados

# Função para capturar banner DNS (porta 53)
def grab_dns_banner(target):
    """Captura informações DNS (consulta A)."""
    try:
        result = dns.resolver.resolve(target, 'A')  # Consulta DNS tipo 'A'
        return ', '.join([str(ip.address) for ip in result])  # Retorna os endereços IPs encontrados
    except dns.resolver.NoAnswer:
        return "Nenhuma resposta encontrada"
    except dns.resolver.NXDOMAIN:
        return "Domínio não encontrado"
    except Exception as e:
        return f"Erro ao consultar DNS: {e}"

# Função para capturar o banner de um serviço na porta especificada
def grab_banner(target, port):
    """Tenta capturar o banner de uma porta, usando SSL para HTTPS (porta 443)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # Tempo limite de 2 segundos

        # Usando SSL para conexões HTTPS (porta 443)
        if port == 443:
            context = ssl.create_default_context()
            with context.wrap_socket(sock, server_hostname=target) as ssock:
                ssock.connect((target, port))
                banner = ssock.recv(1024).decode().strip()
        else:
            sock.connect((target, port))
            sock.send(b'Hello\r\n')
            banner = sock.recv(1024).decode().strip()

        sock.close()

        return banner if banner else "Banner vazio"
    except socket.timeout:
        return "Timeout: Não foi possível conectar ou obter resposta a tempo"
    except socket.error as e:
        return f"Erro de conexão: {e}"
    except Exception as e:
        return f"Erro inesperado: {e}"

if __name__ == "__main__":
    try:
        # Configurações do usuário
        timeout, max_threads = get_user_config()
        
        target = input("Digite o IP ou domínio para escanear: ")
        ports = input("Digite as portas que deseja verificar (separadas por vírgula): ")
        ports = [int(port.strip()) for port in ports.split(",")]

        logging.info(f"Escaneando {target} nas portas: {ports}")
        scan_ports_with_progress(target, ports, timeout, max_threads)
    except ValueError:
        logging.error("[Erro] Entrada inválida. Certifique-se de fornecer números válidos para as portas.")
        print("[Erro] Entrada inválida. Certifique-se de fornecer números válidos para as portas.")
    except Exception as e:
        logging.error(f"[Erro] Ocorreu um erro inesperado: {e}")
        print(f"[Erro] Ocorreu um erro inesperado: {e}")
