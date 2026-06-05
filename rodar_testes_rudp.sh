#!/bin/bash
RUNS=10

for i in $(seq 1 $RUNS); do
    echo "Execucao $i..."
    python3 /app/rudp_cliente.py
    sleep 1
done