import sys
import os
import argparse
from tqdm import tqdm  # Importando o tqdm para a barra de progresso
import csv  # Importando a biblioteca para exportar resultados para CSV

# Adiciona o diretório pai de 'src' ao sys.path para garantir que os módulos em 'src' sejam encontrados
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.port_scanner import scan_ports  # Agora o Python pode encontrar o módulo corretamente

def parse_args():
    # Cria o parser de argumentos
    parser = argparse.ArgumentParser(description="Scanner de portas simples.")
    
    # Adiciona os argumentos que o usuário deve passar
    parser.add_argument('target', help="IP ou domínio a ser escaneado.")  # O alvo (IP ou domínio)
    parser.add_argument('ports', help="Portas a serem verificadas, separadas por vírgula ou intervalo.")
    
    # Argumentos opcionais com valores padrão
    parser.add_argument('--timeout', type=int, default=1, help="Tempo limite de conexão em segundos (padrão: 1).")
    parser.add_argument('--threads', type=int, default=10, help="Número de threads para escanear as portas em paralelo (padrão: 10).")
    
    return parser.parse_args()

def scan_ports_with_progress(target, ports, timeout, threads):
    results = {}
    for port in tqdm(ports, desc="Escaneando portas", unit="porta"):
        result = scan_ports(target, [port], timeout, threads)
        if result:
            print(f"A porta {port} está aberta em {target}.")
        else:
            print(f"A porta {port} está fechada em {target}.")
        results[port] = "Aberta" if result else "Fechada"
    
    export_results_to_csv(results)
    return results


def export_results_to_csv(results):
    # Exporta os resultados para um arquivo CSV
    with open('scan_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Porta', 'Status'])  # Cabeçalho
        for port, status in results.items():
            writer.writerow([port, status])  # Escreve os resultados

def main():
    # Parseia os argumentos passados na linha de comando
    args = parse_args()

    # Converte as portas fornecidas em uma lista de inteiros
    ports = [int(port.strip()) for port in args.ports.split(",")]

    # Chama a função de escaneamento com a barra de progresso
    scan_ports_with_progress(args.target, ports, args.timeout, args.threads)

if __name__ == "__main__":
    main()
