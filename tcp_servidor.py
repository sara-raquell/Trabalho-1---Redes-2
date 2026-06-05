import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 5000))
server.listen(1)

while True:
    print("Esperando conexao...")
    conn, addr = server.accept()
    print(f"Conectado com {addr}")

    cabecalho = conn.recv(1024).decode()
    partes = cabecalho.split('|')

    auth    = partes[0].split(':')[1]
    arquivo = partes[1].split(':')[1]
    tamanho = int(partes[2].split(':')[1])

    print(f"Auth recebido: {auth}")
    print(f"Arquivo: {arquivo} ({tamanho} bytes)")

    conn.send(b"OK")

    recebido = 0
    with open(f"recebido_{arquivo}", 'wb') as f:
        while recebido < tamanho:
            dados = conn.recv(1024)
            if not dados:
                break
            f.write(dados)
            recebido += len(dados)

    print(f"Arquivo recebido! Salvo como: recebido_{arquivo}")
    conn.close()