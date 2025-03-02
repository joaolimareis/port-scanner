import socket
import ssl
import dns.resolver

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

def grab_dns_banner(target):
    """Captura informações DNS (consulta A)."""
    try:
        # Verifica se o 'target' parece ser um IP ou domínio
        if target.replace(".", "").isdigit():  # Verifica se é um IP
            return f"Não é possível resolver IP diretamente com DNS. Insira um domínio válido."

        result = dns.resolver.resolve(target, 'A')  # Consulta DNS tipo 'A'
        return ', '.join([str(ip.address) for ip in result])  # Retorna os endereços IPs encontrados
    except dns.resolver.NoAnswer:
        return "Nenhuma resposta encontrada"
    except dns.resolver.NXDOMAIN:
        return "Domínio não encontrado"
    except Exception as e:
        return f"Erro ao consultar DNS: {e}"

def scan_ports(target, ports):
    """
    Escaneia múltiplas portas e captura banners.
    Também tenta capturar informações DNS se a porta for 53 (DNS).
    """
    for port in ports:
        if port == 53:
            # Captura informações DNS para a porta 53
            dns_banner = grab_dns_banner(target)
            print(f"Porta {port} (DNS): {dns_banner}")
        else:
            # Captura o banner para outras portas
            banner = grab_banner(target, port)
            print(f"Porta {port}: {banner}")

if __name__ == "__main__":
    target = input("Digite o IP ou domínio para escanear: ")
    ports = input("Digite as portas que deseja verificar (separadas por vírgula): ")
    ports = [int(port.strip()) for port in ports.split(",")]

    scan_ports(target, ports)
