FROM ollama/ollama:0.1.32

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

COPY models-gpu.txt models-cpu.txt /root/

COPY entrypoint.sh /root/
RUN chmod +x /root/entrypoint.sh

ENTRYPOINT ["/root/entrypoint.sh"]
