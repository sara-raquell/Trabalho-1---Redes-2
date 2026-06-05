import socket
import struct
import hashlib
import zlib
import os
import time
import csv

MATRICULA = "20249017305"
NOME = "Sara Raquel de Castro Moraes"
ARQUIVO = "arquivo_teste.txt"
CENARIO = "B"
HOST = '10.0.0.2'
PORT = 5001
TIMEOUT = 2.0
CHUNK_SIZE = 1024

def get_auth_hash():
    raw = MATRICULA + NOME
    return hashlib.sha256(raw.encode()).hexdigest()

def monta_pacote(seq, tipo, dados):
    auth = get_auth_hash().encode()[:64].ljust(64, b'\x00')
    checksum = zlib.crc32(dados)
    header = struct.pack('!64sIBI', auth, seq, tipo, checksum)
    return header + dados

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(TIMEOUT)

tamanho = os.path.getsize(ARQUIVO)
seq = 0
inicio = time.time()

dados_info = f"{ARQUIVO}|{tamanho}".encode()
pacote = monta_pacote(seq, 0x01, dados_info)

while True:
    sock.sendto(pacote, (HOST, PORT))
    try:
        ack, _ = sock.recvfrom(128)
        ack_seq = struct.unpack('!I', ack)[0]
        if ack_seq == seq:
            seq += 1
            break
    except socket.timeout:
        print(f"Timeout no pacote {seq}, reenviando...")

with open(ARQUIVO, 'rb') as f:
    while True:
        chunk = f.read(CHUNK_SIZE)
        if not chunk:
            break

        pacote = monta_pacote(seq, 0x01, chunk)

        while True: 
            sock.sendto(pacote, (HOST, PORT))
            try:
                ack, _ = sock.recvfrom(128)
                ack_seq = struct.unpack('!I', ack)[0]
                if ack_seq == seq:
                    seq += 1
                    break
            except socket.timeout:
                print(f"Timeout no pacote {seq}, reenviando...")

fin = monta_pacote(seq, 0x03, b'')
sock.sendto(fin, (HOST, PORT))

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
    writer.writerow([CENARIO, 'RUDP', f"{tempo:.4f}", f"{throughput:.2f}"])

print(f"Dados salvos em {arquivo_csv}!")
sock.close()