#!/bin/bash
# Healthcheck script for unified Hoplias container

# Check if supervisor is running
if ! pgrep -x supervisord > /dev/null; then
    echo "Supervisor is not running"
    exit 1
fi

# Check if Python services are running
services=("hoplias-gateway" "hoplias-api-service" "hoplias-segmentation" "hoplias-classification" "hoplias-ideogram")
for service in "${services[@]}"; do
    if ! supervisorctl status $service | grep -q RUNNING; then
        echo "Service $service is not running"
        exit 1
    fi
done

# Check infrastructure services
# Redis
if ! nc -z localhost ${REDIS_PORT:-6379} 2>/dev/null; then
    echo "Redis is not responding"
    exit 1
fi

# RabbitMQ
if ! nc -z localhost ${RABBITMQ_PORT:-5672} 2>/dev/null; then
    echo "RabbitMQ is not responding"
    exit 1
fi

# MongoDB
if ! nc -z localhost ${MONGODB_PORT:-27017} 2>/dev/null; then
    echo "MongoDB is not responding"
    exit 1
fi

# Nginx
if ! nc -z localhost ${NGINX_PORT:-8080} 2>/dev/null; then
    echo "Nginx is not responding"
    exit 1
fi

# All checks passed
exit 0

