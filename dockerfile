FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    python3 \
    iproute2 \
    tcpdump
WORKDIR /app
COPY . .