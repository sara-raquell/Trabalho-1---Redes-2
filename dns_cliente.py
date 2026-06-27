import socket
import os

DNS_HOST = '10.0.0.4'
DNS_PORT = 53

def resolve(nome):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3.0)
    
    id_query = os.urandom(2)
    nome_bytes = nome.encode()
    query = id_query + bytes([len(nome_bytes)]) + nome_bytes
    
    tentativas = 0
    while tentativas < 3:
        try:
            sock.sendto(query, (DNS_HOST, DNS_PORT))
            resposta, _ = sock.recvfrom(512)
            
            tipo = resposta[2]
            if tipo == 0x01:
                ip_bytes = resposta[-4:]
                ip = socket.inet_ntoa(ip_bytes)
                print(f"DNS resolveu: {nome} -> {ip}")
                return ip
            else:
                print(f"DNS: nome nao encontrado")
                return None
        except socket.timeout:
            tentativas += 1
            print(f"DNS timeout, tentativa {tentativas}/3...")
    
    return None

if __name__ == "__main__":
    ip = resolve("webserver.local")
    print(f"IP obtido: {ip}")