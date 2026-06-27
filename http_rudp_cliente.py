import socket
import struct
import zlib
import hashlib
import time
import csv
import os
from dns_cliente import resolve

MATRICULA = "20249017305"
NOME = "Sara Raquel de Castro Moraes"
CENARIO = "B"
PORT = 8081
TIMEOUT = 2.0
CHUNK_SIZE = 1024
ARQUIVOS = ['arquivo_100kb.txt', 'arquivo_1mb.txt', 'arquivo_10mb.txt']

def get_auth_hash():
    raw = MATRICULA + NOME
    return hashlib.sha256(raw.encode()).hexdigest()

def monta_pacote(seq, tipo, dados):
    auth = get_auth_hash().encode()[:64].ljust(64, b'\x00')
    checksum = zlib.crc32(dados)
    header = struct.pack('!64sIBI', auth, seq, tipo, checksum)
    return header + dados

def http_get_rudp(host, caminho):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    request = (
        f"GET /{caminho} HTTP/1.1\r\n"
        f"Host: webserver.local\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode()

    seq = 0
    for i in range(0, len(request), CHUNK_SIZE):
        chunk = request[i:i+CHUNK_SIZE]
        pkt = monta_pacote(seq, 0x01, chunk)
        while True:
            sock.sendto(pkt, (host, PORT))
            try:
                ack, _ = sock.recvfrom(4096)
                if len(ack) != 4:
                    continue
                ack_seq = struct.unpack('!I', ack)[0]
                if ack_seq == seq:
                    seq += 1
                    break
            except socket.timeout:
                print(f"Timeout pacote {seq}, reenviando...")

    fin = monta_pacote(seq, 0x03, b'')
    sock.sendto(fin, (host, PORT))

    sock.settimeout(10.0)

    resposta = b""
    esperando_seq = 0
    timeouts_seguidos = 0
    while True:
        try:
            pacote, addr = sock.recvfrom(4096)
            timeouts_seguidos = 0 

            if len(pacote) < 73:
                continue

            tipo = pacote[68]
            seq_r = struct.unpack('!I', pacote[64:68])[0]
            dados = pacote[73:]

            if tipo == 0x03:
                break
            if tipo == 0x01 and seq_r == esperando_seq:
                resposta += dados
                ack = struct.pack('!I', seq_r)
                sock.sendto(ack, addr)
                esperando_seq += 1
            elif tipo == 0x01 and seq_r < esperando_seq:
                ack = struct.pack('!I', seq_r)
                sock.sendto(ack, addr)
        except socket.timeout:
            timeouts_seguidos += 1
            print(f"Timeout aguardando resposta (tentativa {timeouts_seguidos})...")
            if timeouts_seguidos >= 5:
                print("Servidor não respondeu após 5 timeouts, encerrando.")
                break

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
    print(f"\nTestando {arquivo} via R-UDP...")
    inicio = time.time()
    resposta = http_get_rudp(ip, arquivo)
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
        writer.writerow([CENARIO, 'RUDP', arquivo, f"{tempo_dns:.4f}",
                        f"{tempo_http:.4f}", f"{tempo_dns+tempo_http:.4f}",
                        f"{throughput:.2f}", status])

print("\nDados salvos!")