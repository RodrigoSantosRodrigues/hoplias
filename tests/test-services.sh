#!/bin/bash
# Service connectivity test script

set -e

CONTAINER_NAME=${CONTAINER_NAME:-hoplias-test}

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[TEST]${NC} $1"
}

error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

test_port() {
    local service=$1
    local port=$2
    local host=${3:-localhost}
    
    log "Testing $service on $host:$port..."
    if docker exec $CONTAINER_NAME nc -z $host $port 2>/dev/null; then
        success "$service is accessible on port $port"
        return 0
    else
        error "$service is not accessible on port $port"
        return 1
    fi
}

test_http() {
    local service=$1
    local url=$2
    
    log "Testing HTTP endpoint: $url..."
    if curl -f -s -m 5 $url > /dev/null 2>&1; then
        success "$service HTTP endpoint is accessible"
        return 0
    else
        warn "$service HTTP endpoint may not be ready"
        return 1
    fi
}

main() {
    log "Testing service connectivity..."
    
    # Infrastructure services
    test_port "Redis" 6379
    test_port "RabbitMQ" 5672
    test_port "RabbitMQ Management" 15672
    test_port "MongoDB" 27017
    test_port "Elasticsearch" 9200 || warn "Elasticsearch may not be running"
    test_port "Graylog" 9001 || warn "Graylog may not be running"
    test_port "Prometheus" 9090 || warn "Prometheus may not be running"
    test_port "Grafana" 3000 || warn "Grafana may not be running"
    test_port "Nginx" 8080
    
    # Python services
    test_port "Gateway" 8001
    test_port "API Service" 8005
    test_port "Segmentation" 8003
    test_port "Classification" 8004
    test_port "Ideogram" 8007
    
    # HTTP endpoints
    test_http "Gateway" "http://localhost:8001/"
    test_http "API Service" "http://localhost:8005/docs"
    test_http "Nginx" "http://localhost:8080/"
    
    log "Service connectivity tests completed"
}

main

