#!/bin/bash

# Lista serviços do arquivo específico
services=$(docker compose -f docker-compose-less.yml config --services)

for service in $services; do
    echo "🔧 Building: $service"
    docker compose -f docker-compose-less.yml build "$service"
    
    echo "🚀 Starting: $service"
    docker compose -f docker-compose-less.yml up -d "$service"
    
    echo "✅ Service '$service' started."
done

echo "✅ All services processed!"
