#!/bin/bash

services=$(docker compose config --services)

for service in $services; do
    echo "🔧 Building: $service"
    docker compose build "$service"
    
    echo "🚀 Starting: $service"
    docker compose up -d "$service"
    
    echo "✅ Service '$service' started."
done

echo "✅ Done!."
