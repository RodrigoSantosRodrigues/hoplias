# Hoplias Unified Container

Imagem Docker unificada e otimizada contendo todos os serviços do Hoplias em um único container.

## Características

- **Otimizado**: Multi-stage build com otimizações de tamanho, camadas e memória
- **Genérico**: Suporte completo a override de variáveis de ambiente e portas
- **Leve**: Imagem otimizada com remoção de arquivos desnecessários
- **Funcional**: Todos os serviços integrados e testados

## Build da Imagem

```bash
docker build -f Dockerfile.unified-optimized -t hoplias-unified:latest .
```

## Uso Básico

```bash
docker run -d \
  --name hoplias \
  -p 8001:8001 \
  -p 8003:8003 \
  -p 8004:8004 \
  -p 8005:8005 \
  -p 8007:8007 \
  -p 8080:8080 \
  -p 6379:6379 \
  -p 5672:5672 \
  -p 15672:15672 \
  -p 27017:27017 \
  hoplias-unified:latest
```

## Variáveis de Ambiente

### Portas (com valores padrão)

- `GATEWAY_PORT=8001` - Porta do Gateway
- `API_PORT=8005` - Porta do API Service
- `SEGMENTATION_PORT=8003` - Porta do Segmentation Service
- `CLASSIFICATION_PORT=8004` - Porta do Classification Service
- `IDEOGRAM_PORT=8007` - Porta do Ideogram Service
- `NGINX_PORT=8080` - Porta do Nginx
- `REDIS_PORT=6379` - Porta do Redis
- `RABBITMQ_PORT=5672` - Porta do RabbitMQ
- `RABBITMQ_MANAGEMENT_PORT=15672` - Porta de gerenciamento do RabbitMQ
- `MONGODB_PORT=27017` - Porta do MongoDB
- `ELASTICSEARCH_PORT=9200` - Porta do Elasticsearch
- `GRAYLOG_PORT=9001` - Porta do Graylog
- `PROMETHEUS_PORT=9090` - Porta do Prometheus
- `GRAFANA_PORT=3000` - Porta do Grafana

### Credenciais

- `RABBIT_USER=guest` - Usuário do RabbitMQ
- `RABBIT_PASSWORD=guest` - Senha do RabbitMQ
- `REDIS_PASSWORD=` - Senha do Redis (vazio por padrão)
- `DB_USER=admin` - Usuário do MongoDB
- `DB_PASSWORD=root` - Senha do MongoDB
- `DB_API=hoplias` - Nome do banco de dados

### Outras Variáveis

Todas as variáveis do arquivo `.env` podem ser sobrescritas passando `-e VAR=value` ao executar o container.

## Exemplo com Override de Variáveis

```bash
docker run -d \
  --name hoplias \
  -e GATEWAY_PORT=9001 \
  -e API_PORT=9002 \
  -e RABBIT_USER=myuser \
  -e RABBIT_PASSWORD=mypass \
  -e DB_PASSWORD=securepass \
  -p 9001:9001 \
  -p 9002:9002 \
  hoplias-unified:latest
```

## Usando Arquivo .env

```bash
docker run -d \
  --name hoplias \
  --env-file .env \
  -p 8001:8001 \
  hoplias-unified:latest
```

## Volumes (Opcional)

Para persistência de dados:

```bash
docker run -d \
  --name hoplias \
  -v hoplias-redis:/data/redis \
  -v hoplias-mongodb:/data/mongodb \
  -v hoplias-rabbitmq:/data/rabbitmq \
  hoplias-unified:latest
```

## Healthcheck

O container inclui um healthcheck automático que verifica:

- Supervisor está rodando
- Todos os serviços Python estão ativos
- Serviços de infraestrutura respondem nas portas configuradas

Para verificar manualmente:

```bash
docker exec hoplias /app/scripts/healthcheck.sh
```

## Logs

Ver logs de todos os serviços:

```bash
docker logs hoplias
```

Ver logs de um serviço específico via supervisor:

```bash
docker exec hoplias supervisorctl tail -f hoplias-gateway
```

## Serviços Incluídos

### Serviços Python (gerenciados pelo Supervisor)

- **hoplias-gateway** - Gateway API (porta 8001)
- **hoplias-api-service** - API Service (porta 8005)
- **hoplias-segmentation** - Segmentation Service (porta 8003)
- **hoplias-classification** - Classification Service (porta 8004)
- **hoplias-ideogram** - Ideogram Service (porta 8007)

### Serviços de Infraestrutura

- **Redis** - Cache e filas (porta 6379)
- **RabbitMQ** - Message broker (porta 5672, management 15672)
- **MongoDB** - Banco de dados (porta 27017)
- **Elasticsearch** - Busca e indexação (porta 9200)
- **Graylog** - Agregação de logs (porta 9001)
- **Prometheus** - Métricas (porta 9090)
- **Grafana** - Visualização de métricas (porta 3000)
- **Nginx** - Reverse proxy (porta 8080)

## Testes

### Executar todos os testes

```bash
cd tests
chmod +x *.sh
./test-unified-image.sh
```

### Testar conectividade dos serviços

```bash
./tests/test-services.sh
```

### Testar override de variáveis

```bash
./tests/test-env-override.sh
```

## Otimizações Aplicadas

1. **Multi-stage build**: Reduz tamanho final da imagem
2. **Consolidação de dependências**: Dependências Python comuns instaladas uma vez
3. **Remoção de arquivos desnecessários**: Documentação, man pages, caches
4. **Limpeza de camadas**: Comandos RUN combinados quando possível
5. **Imagens base otimizadas**: Uso de imagens slim/alpine quando possível
6. **Limites de memória**: Configurações JVM otimizadas para serviços Java

## Troubleshooting

### Container não inicia

Verifique os logs:

```bash
docker logs hoplias
```

### Serviço específico não está rodando

Verifique status do supervisor:

```bash
docker exec hoplias supervisorctl status
```

Reinicie um serviço:

```bash
docker exec hoplias supervisorctl restart hoplias-gateway
```

### Porta já em uso

Altere a porta usando variável de ambiente:

```bash
docker run -d -e GATEWAY_PORT=9001 -p 9001:9001 hoplias-unified:latest
```

### Problemas de memória

A imagem foi otimizada para uso mínimo de memória. Se necessário, ajuste limites:

```bash
docker run -d --memory="4g" --memory-swap="4g" hoplias-unified:latest
```

## Requisitos

- Docker 20.10+
- Mínimo 4GB RAM recomendado
- Mínimo 10GB espaço em disco

## Licença

Ver arquivo LICENSE no diretório raiz do projeto.

