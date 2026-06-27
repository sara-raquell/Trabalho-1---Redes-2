# Análise de Desempenho TCP vs R-UDP
**Disciplina:** Redes de Computadores II — 2026-1  
**Aluna:** Sara Raquel de Castro Moraes  
**Matrícula:** 20249017305  
**Instituição:** UFPI — Campus Senador Helvídio Nunes de Barros

---

## Sobre o Projeto
Implementação e comparação de dois sistemas de transferência de arquivos:
- **TCP:** Usando sockets TCP padrão do Python
- **R-UDP:** UDP com confiabilidade implementada manualmente (Stop-and-Wait)

---

## Estrutura do Repositório

├── tcp_cliente.py          -  Cliente TCP

├── tcp_servidor.py         -  Servidor TCP

├── rudp_cliente.py         -  Cliente R-UDP (Stop-and-Wait)

├── rudp_servidor.py        -  Servidor R-UDP

├── analyze.py              -  Geração de gráficos (Pandas/Matplotlib)

├── rodar_testes.sh         - Script para 10 execuções TCP

├── rodar_testes_rudp.sh    - Script para 10 execuções R-UDP

├── docker-compose.yml      - Configuração dos containers

├── Dockerfile              - Imagem Ubuntu com Python e tcpdump

├── resultados.csv          - Dados coletados nos testes

├── grafico_comparativo.png - Gráfico de barras TCP vs R-UDP

├── grafico_degradacao.png  - Gráfico de degradação por cenário

├── captura_tcp_A.pcap      - Captura Wireshark — TCP Cenário A

└── captura_rudp_A.pcap     - Captura Wireshark — R-UDP Cenário A

---

## Como Executar

### 1. Subir os containers
```bash
docker compose up --build
```

### 2. Aplicar simulação de rede (escolha o cenário)
```bash
# Cenário A — 0% perda / 10ms delay
docker exec -it cliente tc qdisc add dev eth0 root netem delay 10ms loss 0%

# Cenário B — 5% perda / 50ms delay
docker exec -it cliente tc qdisc add dev eth0 root netem delay 50ms loss 5%

# Cenário C — 10% perda / 100ms delay
docker exec -it cliente tc qdisc add dev eth0 root netem delay 100ms loss 10%
```

### 3. Rodar o servidor (em um terminal)
```bash
# TCP
docker exec -it servidor python3 /app/tcp_servidor.py

# R-UDP
docker exec -it servidor python3 /app/rudp_servidor.py
```

### 4. Rodar os testes (em outro terminal)
```bash
# TCP — 10 execuções
docker exec -it cliente bash /app/rodar_testes.sh

# R-UDP — 10 execuções
docker exec -it cliente bash /app/rodar_testes_rudp.sh
```

### 5. Capturar tráfego com tcpdump
```bash
docker exec -d servidor tcpdump -i eth0 -w /app/captura.pcap
```

### 6. Gerar gráficos
```bash
pip install pandas matplotlib numpy
python analyze.py
```

---

## Cenários de Teste

| Cenário | Perda | Delay |
|---------|-------|-------|
| A | 0% | 10ms |
| B | 5% | 50ms |
| C | 10% | 100ms |

---

## Resultados

| Cenário | Protocolo | Média (KB/s) | Desvio Padrão |
|---------|-----------|-------------|---------------|
| A | TCP | 16485 | 9440 |
| A | R-UDP | 88,3 | 26,6 |
| B | TCP | 822 | 1079 |
| B | R-UDP | 6,79 | 0,63 |
| C | TCP | 61 | 19 |
| C | R-UDP | 3,20 | 0,17 |

---

## Autenticação
Todos os pacotes contêm o campo `X-Custom-Auth` com o hash SHA-256:
- SHA-256("20249017305Sara Raquel de Castro Moraes")
= c213048df96f49db17b24cef7e6512c265c30dbcf1eefe0b04b92170818eedf4


---

## 3ª Avaliação — Evolução: Miniservidor HTTP sobre R-UDP/TCP com DNS

### Sobre

Evolução do sistema anterior para uma arquitetura web completa com:
- **Módulo DNS local** — servidor/cliente DNS minimalista sobre UDP (porta 53)
- **Miniservidor HTTP/1.1** — suporte a GET, 404, cabeçalhos padrão e X-Custom-Auth, operando sobre TCP (porta 8080) e R-UDP (porta 8081)

### Arquitetura

[Cliente] → DNS query (UDP:53) → [Servidor DNS]

[Cliente] → HTTP GET (TCP:8080 ou R-UDP:8081) → [Servidor Web]

Três containers Docker na subnet `10.0.0.0/24`:
- `10.0.0.2` — Servidor Web
- `10.0.0.3` — Cliente
- `10.0.0.4` — Servidor DNS

### Novos Arquivos

├── http_tcp_servidor.py   - Miniservidor HTTP/1.1 sobre TCP (porta 8080)

├── http_rudp_servidor.py  - Miniservidor HTTP/1.1 sobre R-UDP (porta 8081)

├── http_cliente.py        - Cliente HTTP (TCP e R-UDP)

├── dns_servidor.py        - Servidor DNS minimalista (UDP porta 53)

├── dns_cliente.py         - Cliente DNS

├── hosts.txt              - Arquivo de zona DNS local

├── resultados_http.csv    - Dados coletados nos testes

└── captura.pcap           - Captura Wireshark — sequência DNS → HTTP

### Como Executar

#### 1. Subir o servidor DNS
```bash
docker exec -it dns python3 /app/dns_servidor.py
```

#### 2. Subir o servidor HTTP
```bash
# TCP
docker exec -it servidor python3 /app/http_tcp_servidor.py

# R-UDP
docker exec -it servidor python3 /app/http_rudp_servidor.py
```

#### 3. Rodar os testes
```bash
docker exec -it cliente bash /app/rodar_testes_http.sh tcp
docker exec -it cliente bash /app/rodar_testes_http.sh rudp
```

### Resultados

| Cenário | Protocolo | Arquivo | Média (KB/s) | Desvio | Mín | Máx |
|---------|-----------|---------|-------------|--------|-----|-----|
| A | TCP | 100 KB | 1762 | 179 | 1404 | 1977 |
| A | TCP | 1 MB | 3855 | 282 | 3257 | 4293 |
| A | TCP | 10 MB | 553 | 20 | 520 | 584 |
| A | R-UDP | 100 KB | 139 | 156 | 88 | 582 |
| A | R-UDP | 1 MB | 89 | 4 | 86 | 97 |
| A | R-UDP | 10 MB | 71 | 0,6 | 69 | 72 |
| B | TCP | 100 KB | 413 | 121 | 77 | 467 |
| B | TCP | 1 MB | 2008 | 268 | 1268 | 2220 |
| B | TCP | 10 MB | 1214 | 93 | 1103 | 1411 |
| B | R-UDP | 100 KB | 6,34 | 0,07 | 6,23 | 6,45 |
| B | R-UDP | 1 MB | 7,73 | 0,04 | 7,66 | 7,80 |
| B | R-UDP | 10 MB | 6,25 | 0,01 | 6,23 | 6,27 |
| C | TCP | 100 KB | 199 | 46 | 112 | 238 |
| C | TCP | 1 MB | 1096 | 64 | 940 | 1142 |
| C | TCP | 10 MB | 1116 | 47 | 1014 | 1201 |
| C | R-UDP | 100 KB | 1,91 | 0,08 | 1,79 | 2,04 |
| C | R-UDP | 1 MB | 3,34 | 0,06 | 3,25 | 3,43 |
| C | R-UDP | 10 MB | 3,27 | 0,04 | 3,20 | 3,33 |

### Tempo de Resolução DNS

| Cenário | Tempo médio |
|---------|-------------|
| A | 0,013 s |
| B | 0,106 s |
| C | 0,213 s |
