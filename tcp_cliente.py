import socket
import os
import hashlib
import time
import csv

MATRICULA = "20249017305"
NOME = "Sara Raquel de Castro Moraes"
ARQUIVO = "arquivo_teste.txt"
CENARIO = "C"  

def get_auth_hash():
    raw = MATRICULA + NOME
    return hashlib.sha256(raw.encode()).hexdigest()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('10.0.0.2', 5000))

auth = get_auth_hash()
tamanho = os.path.getsize(ARQUIVO)
cabecalho = f"X-Custom-Auth:{auth}|Filename:{ARQUIVO}|Size:{tamanho}"
client.send(cabecalho.encode())
resposta = client.recv(1024)
print(f"Servidor respondeu: {resposta.decode()}")

inicio = time.time()
with open(ARQUIVO, 'rb') as f:
    while True:
        dados = f.read(1024)
        if not dados:
            break
        client.send(dados)

fim = time.time()
tempo = fim - inicio
throughput = (tamanho / 1024) / tempo  

print(f"Arquivo enviado!")
print(f"Tempo: {tempo:.4f} segundos")
print(f"Throughput: {throughput:.2f} KB/s")

arquivo_csv = "resultados.csv"
arquivo_existe = os.path.exists(arquivo_csv)

with open(arquivo_csv, 'a', newline='') as f:
    writer = csv.writer(f)
    if not arquivo_existe:
        writer.writerow(['cenario', 'protocolo', 'tempo_s', 'throughput_kbps'])
    writer.writerow([CENARIO, 'TCP', f"{tempo:.4f}", f"{throughput:.2f}"])

print(f"Dados salvos em {arquivo_csv}!")
client.close()