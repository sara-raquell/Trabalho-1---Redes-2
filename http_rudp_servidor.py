import socket
import struct
import hashlib
import zlib
import os

HOST = '0.0.0.0'
PORT = 8081
MATRICULA = "20249017305"
NOME = "Sara Raquel de Castro Moraes"
CHUNK_SIZE = 1024
TIMEOUT = 2.0

def get_auth_hash():
    raw = MATRICULA + NOME
    return hashlib.sha256(raw.encode()).hexdigest()

def monta_pacote(seq, tipo, dados, auth):
    auth_bytes = auth.encode()[:64].ljust(64, b'\x00')
    checksum = zlib.crc32(dados)
    header = struct.pack('!64sIBI', auth_bytes, seq, tipo, checksum)
    return header + dados

def processa_request(request):
    linhas = request.split('\r\n')
    primeira_linha = linhas[0]
    partes = primeira_linha.split(' ')
    if len(partes) < 2:
        return None
    caminho = partes[1].lstrip('/')
    if not caminho:
        caminho = 'index.html'
    return caminho

def monta_resposta_http(caminho):
    auth = get_auth_hash()
    path = f'/app/{caminho}'
    if os.path.exists(path):
        with open(path, 'rb') as f:
            corpo = f.read()
        content_type = 'text/html' if caminho.endswith('.html') else 'application/octet-stream'
        cabecalho = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(corpo)}\r\n"
            f"X-Custom-Auth: {auth}\r\n"
            f"\r\n"
        ).encode()
        return cabecalho + corpo
    else:
        corpo = b"<h1>404 Not Found</h1>"
        cabecalho = (
            f"HTTP/1.1 404 Not Found\r\n"
            f"Content-Type: text/html\r\n"
            f"Content-Length: {len(corpo)}\r\n"
            f"X-Custom-Auth: {auth}\r\n"
            f"\r\n"
        ).encode()
        return cabecalho + corpo

def parse_pacote(pacote):
    if len(pacote) < 73:
        return None
    seq      = struct.unpack('!I', pacote[64:68])[0]
    tipo     = pacote[68]
    checksum = struct.unpack('!I', pacote[69:73])[0]
    dados    = pacote[73:]
    if zlib.crc32(dados) != checksum:
        return None
    return seq, tipo, dados

auth = get_auth_hash()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))
sock.settimeout(None)
print(f"Servidor HTTP/R-UDP rodando na porta {PORT}...")

while True:
    request_buffer = b""
    esperando_seq = 0
    client_addr = None

    while True:
        pacote, addr = sock.recvfrom(4096)
        client_addr = addr

        parsed = parse_pacote(pacote)
        if parsed is None:
            print("Pacote inválido/corrompido, ignorando.")
            continue

        seq, tipo, dados = parsed

        if tipo == 0x01:
            if seq == esperando_seq:
                request_buffer += dados
                ack = struct.pack('!I', seq)
                sock.sendto(ack, client_addr)
                esperando_seq += 1
            else:
                ack = struct.pack('!I', esperando_seq - 1)
                sock.sendto(ack, client_addr)

        elif tipo == 0x03:
            ack = struct.pack('!I', seq)
            sock.sendto(ack, client_addr)
            break

    request_str = request_buffer.decode(errors='replace')
    print(f"Request recebido:\n{request_str[:200]}")

    caminho = processa_request(request_str)
    resposta = monta_resposta_http(caminho)
    print(f"Servindo: {caminho} ({len(resposta)} bytes)")

    sock.settimeout(TIMEOUT)
    seq_resp = 0

    for i in range(0, len(resposta), CHUNK_SIZE):
        chunk = resposta[i:i + CHUNK_SIZE]
        pkt = monta_pacote(seq_resp, 0x01, chunk, auth)

        while True:
            sock.sendto(pkt, client_addr)
            try:
                ack, _ = sock.recvfrom(4096)
                if len(ack) != 4:
                    continue
                ack_seq = struct.unpack('!I', ack)[0]
                if ack_seq == seq_resp:
                    seq_resp += 1
                    break
            except socket.timeout:
                print(f"Timeout aguardando ACK {seq_resp}, reenviando chunk...")

    fin = monta_pacote(seq_resp, 0x03, b'', auth)
    sock.sendto(fin, client_addr)

    sock.settimeout(None)
    print("Resposta enviada com sucesso!\n")