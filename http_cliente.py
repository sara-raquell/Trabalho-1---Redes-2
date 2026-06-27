import socket
import time
import csv
import os
from dns_cliente import resolve

CENARIO = "C"
ARQUIVOS = ['arquivo_100kb.txt', 'arquivo_1mb.txt', 'arquivo_10mb.txt']

def http_get(host, porta, caminho='/'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, porta))
    
    request = (
        f"GET /{caminho} HTTP/1.1\r\n"
        f"Host: webserver.local\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    
    sock.send(request.encode())
    
    resposta = b""
    while True:
        dados = sock.recv(4096)
        if not dados:
            break
        resposta += dados
    
    sock.close()
    return resposta

print("Resolvendo nome via DNS...")
inicio_dns = time.time()
ip = resolve("webserver.local")
fim_dns = time.time()
tempo_dns = fim_dns - inicio_dns
print(f"DNS: {ip} em {tempo_dns:.4f}s")

arquivo_csv = "resultados_http.csv"
arquivo_existe = os.path.exists(arquivo_csv)

for arquivo in ARQUIVOS:
    print(f"\nTestando {arquivo}...")
    inicio = time.time()
    resposta = http_get(ip, 8080, arquivo)
    fim = time.time()
    tempo_http = fim - inicio
    
    status = resposta.split(b'\r\n')[0].decode() if resposta else "Erro"
    tamanho = len(resposta)
    throughput = (tamanho / 1024) / tempo_http if tempo_http > 0 else 0
    
    print(f"Status: {status}")
    print(f"Tamanho recebido: {tamanho} bytes")
    print(f"Tempo HTTP: {tempo_http:.4f}s")
    print(f"Throughput: {throughput:.2f} KB/s")
    print(f"Tempo total: {tempo_dns + tempo_http:.4f}s")

    with open(arquivo_csv, 'a', newline='') as f:
        writer = csv.writer(f)
        if not arquivo_existe:
            writer.writerow(['cenario', 'protocolo', 'arquivo', 'tempo_dns', 
                           'tempo_http', 'tempo_total', 'throughput_kbps', 'status'])
            arquivo_existe = True
        writer.writerow([CENARIO, 'TCP', arquivo, f"{tempo_dns:.4f}",
                        f"{tempo_http:.4f}", f"{tempo_dns+tempo_http:.4f}",
                        f"{throughput:.2f}", status])

print("\nDados salvos!")