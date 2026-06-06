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
