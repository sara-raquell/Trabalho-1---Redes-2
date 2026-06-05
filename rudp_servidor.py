import socket
import struct
import zlib

HOST = '0.0.0.0'
PORT = 5001

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

print("Servidor R-UDP esperando...")

while True:
    esperando_seq = 0
    arquivo_aberto = False
    f = None

    while True:
        pacote, addr = server.recvfrom(2048)

        auth     = pacote[0:64].decode().strip('\x00')
        seq      = struct.unpack('!I', pacote[64:68])[0]
        tipo     = pacote[68]
        checksum = struct.unpack('!I', pacote[69:73])[0]
        dados    = pacote[73:]

        checksum_calculado = zlib.crc32(dados)
        if checksum_calculado != checksum:
            print(f"Pacote {seq} corrompido! Ignorando...")
            continue

        if tipo == 0x03:
            print("Transferência concluída!")
            if f:
                f.close()
            arquivo_aberto = False
            esperando_seq = 0
            print("Servidor R-UDP esperando...")
            break

        if tipo == 0x01:
            if seq == esperando_seq:
                if not arquivo_aberto:
                    nome_arquivo = dados.decode().split('|')[0]
                    f = open(f"recebido_{nome_arquivo}", 'wb')
                    arquivo_aberto = True
                    print(f"Recebendo: {nome_arquivo}")
                else:
                    f.write(dados)

                ack = struct.pack('!I', seq)
                server.sendto(ack, addr)
                esperando_seq += 1
            else:
                ack = struct.pack('!I', esperando_seq)
                server.sendto(ack, addr)