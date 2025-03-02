import csv

def export_results_to_csv(results):
    with open('scan_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Porta', 'Status'])
        for port, status in results.items():
            writer.writerow([port, status])

# Chame esta função após completar o escaneamento
