FROM python:3.11-slim

COPY requirements.txt /app/requirements.txt

COPY . /app

COPY mcp_spec.yml /app/mcp_spec.yml

WORKDIR /app

ENV ENV=production
ENV NODE_VERSION=20.x

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
      | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_VERSION} nodistro main" \
      > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    node -v && npm -v && npx --version && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN node -v && npm -v && npx --version

RUN pip install --no-cache-dir -r requirements.txt

HEALTHCHECK CMD pgrep -f "mcp" || exit 1

CMD ["sh", "-c", "if [ \"$ENV\" = \"development\" ]; then exec mcp dev server.py; else exec mcp run server.py; fi"]
