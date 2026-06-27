import socket
import time

DNS_PORT = 53
HOST = '0.0.0.0'

def carrega_hosts(arquivo='hosts.txt'):
    tabela = {}
    with open(arquivo, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if linha:
                partes = linha.split()
                tabela[partes[0]] = partes[1]
    return tabela

def processa_query(dados, tabela):
    id_query = dados[0:2]
    tamanho = dados[2]
    nome = dados[3:3+tamanho].decode()
    
    print(f"Query DNS para: {nome}")
    
    if nome in tabela:
        ip = tabela[nome]
        print(f"Respondendo: {nome} -> {ip}")
        ip_bytes = socket.inet_aton(ip)
        resposta = id_query + b'\x01' + bytes([tamanho]) + nome.encode() + ip_bytes
    else:
        print(f"Nome nao encontrado: {nome}")
        resposta = id_query + b'\x00' + bytes([tamanho]) + nome.encode()
    
    return resposta

tabela = carrega_hosts('/app/hosts.txt')
print(f"Tabela DNS carregada: {tabela}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, DNS_PORT))
print(f"Servidor DNS rodando na porta {DNS_PORT}...")

while True:
    dados, addr = sock.recvfrom(512)
    resposta = processa_query(dados, tabela)
    sock.sendto(resposta, addr)