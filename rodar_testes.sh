#!/bin/bash
RUNS=10

for i in $(seq 1 $RUNS); do
    echo "Execução $i..."
    python3 /app/tcp_cliente.py
    sleep 1
done