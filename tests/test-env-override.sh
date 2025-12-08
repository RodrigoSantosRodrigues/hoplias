#!/bin/bash
# Environment variable override test script

set -e

IMAGE_NAME=${IMAGE_NAME:-hoplias-unified}
IMAGE_TAG=${IMAGE_TAG:-latest}
CONTAINER_NAME=${CONTAINER_NAME:-hoplias-env-test}

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

cleanup() {
    log "Cleaning up..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
}

trap cleanup EXIT

test_env_var() {
    local var_name=$1
    local expected_value=$2
    local description=$3
    
    log "Testing $description ($var_name=$expected_value)..."
    
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    
    if docker run -d --name $CONTAINER_NAME \
        -e $var_name=$expected_value \
        -p 8001:8001 \
        $IMAGE_NAME:$IMAGE_TAG > /dev/null; then
        sleep 15
        
        actual_value=$(docker exec $CONTAINER_NAME sh -c "echo \$$var_name" 2>/dev/null || echo "")
        
        if [ "$actual_value" = "$expected_value" ]; then
            success "$var_name override works: $actual_value"
            return 0
        else
            error "$var_name override failed. Expected: $expected_value, Got: $actual_value"
            return 1
        fi
    else
        error "Failed to start container with $var_name=$expected_value"
        return 1
    fi
}

main() {
    log "Testing environment variable overrides..."
    
    # Test port overrides
    test_env_var "GATEWAY_PORT" "9001" "Gateway port override"
    test_env_var "API_PORT" "9002" "API port override"
    test_env_var "REDIS_PORT" "6380" "Redis port override"
    
    # Test credential overrides
    test_env_var "RABBIT_USER" "testuser" "RabbitMQ user override"
    test_env_var "RABBIT_PASSWORD" "testpass" "RabbitMQ password override"
    test_env_var "DB_USER" "testdb" "Database user override"
    
    # Test database name override
    test_env_var "DB_API" "testdb" "Database name override"
    
    log "Environment variable override tests completed"
}

main

