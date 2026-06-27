import socket
import hashlib
import os

HOST = '0.0.0.0'
PORT = 8080
MATRICULA = "20249017305"
NOME = "Sara Raquel de Castro Moraes"

def get_auth_hash():
    raw = MATRICULA + NOME
    return hashlib.sha256(raw.encode()).hexdigest()

def processa_request(request):
    linhas = request.split('\r\n')
    primeira_linha = linhas[0]
    partes = primeira_linha.split(' ')
    
    if len(partes) < 2:
        return None
    
    metodo = partes[0]
    caminho = partes[1]
    
    if caminho == '/':
        caminho = '/index.html'
    
    return metodo, caminho.lstrip('/')

def monta_resposta(caminho):
    auth = get_auth_hash()
    
    if os.path.exists(f'/app/{caminho}'):
        with open(f'/app/{caminho}', 'rb') as f:
            corpo = f.read()
        
        if caminho.endswith('.html'):
            content_type = 'text/html'
        else:
            content_type = 'application/octet-stream'
        
        cabecalho = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(corpo)}\r\n"
            f"X-Custom-Auth: {auth}\r\n"
            f"\r\n"
        )
        return cabecalho.encode() + corpo
    else:
        corpo = b"<h1>404 Not Found</h1>"
        cabecalho = (
            f"HTTP/1.1 404 Not Found\r\n"
            f"Content-Type: text/html\r\n"
            f"Content-Length: {len(corpo)}\r\n"
            f"X-Custom-Auth: {auth}\r\n"
            f"\r\n"
        )
        return cabecalho.encode() + corpo

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)
print(f"Miniservidor HTTP rodando na porta {PORT}...")

while True:
    conn, addr = server.accept()
    print(f"Conexão de {addr}")
    
    request = conn.recv(4096).decode()
    print(f"Request:\n{request[:100]}")
    
    resultado = processa_request(request)
    if resultado:
        metodo, caminho = resultado
        print(f"GET /{caminho}")
        resposta = monta_resposta(caminho)
        conn.send(resposta)
    
    conn.close()