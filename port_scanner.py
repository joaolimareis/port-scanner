import socket

def scan_port(target, port):
    """Tenta se conectar a uma porta do alvo para verificar se está aberta."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Tempo limite de 1 segundo para resposta
    result = sock.connect_ex((target, port))  # Retorna 0 se a porta estiver aberta
    sock.close()
    return result == 0  # Retorna True se a porta estiver aberta

if __name__ == "__main__":
    target = input("Digite o IP ou domínio para escanear: ")
    port = int(input("Digite a porta que deseja verificar: "))

    if scan_port(target, port):
        print(f"[+] Porta {port} aberta em {target} ✅")
    else:
        print(f"[-] Porta {port} fechada em {target} ❌")
