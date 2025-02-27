import socket

def scan_port(target, port):
    """Tenta se conectar a uma porta do alvo para verificar se está aberta."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Tempo limite de 1 segundo para resposta
    result = sock.connect_ex((target, port))  # Retorna 0 se a porta estiver aberta
    sock.close()
    return result == 0  # Retorna True se a porta estiver aberta

def scan_ports(target, ports):
    """Escaneia múltiplas portas no alvo fornecido."""
    for port in ports:
        if scan_port(target, port):
            print(f"[+] Porta {port} aberta em {target} ✅")
        else:
            print(f"[-] Porta {port} fechada em {target} ❌")

if __name__ == "__main__":
    target = input("Digite o IP ou domínio para escanear: ")
    ports = input("Digite as portas que deseja verificar (separadas por vírgula): ")
    ports = [int(port.strip()) for port in ports.split(",")]

    scan_ports(target, ports)
