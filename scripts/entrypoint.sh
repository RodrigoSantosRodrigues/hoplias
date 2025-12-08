#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Load environment variables from .env file if it exists
if [ -f /app/.env ]; then
    log "Loading environment variables from /app/.env"
    export $(cat /app/.env | grep -v '^#' | xargs)
fi

# Override with environment variables passed to container
# This allows runtime override of any configuration

# Port configuration with defaults
export GATEWAY_PORT=${GATEWAY_PORT:-8001}
export API_PORT=${API_PORT:-8005}
export SEGMENTATION_PORT=${SEGMENTATION_PORT:-8003}
export CLASSIFICATION_PORT=${CLASSIFICATION_PORT:-8004}
export IDEOGRAM_PORT=${IDEOGRAM_PORT:-8007}
export NGINX_PORT=${NGINX_PORT:-8080}

# Service ports
export REDIS_PORT=${REDIS_PORT:-6379}
export RABBITMQ_PORT=${RABBITMQ_PORT:-5672}
export RABBITMQ_MANAGEMENT_PORT=${RABBITMQ_MANAGEMENT_PORT:-15672}
export MONGODB_PORT=${MONGODB_PORT:-27017}
export ELASTICSEARCH_PORT=${ELASTICSEARCH_PORT:-9200}
export GRAYLOG_PORT=${GRAYLOG_PORT:-9001}
export PROMETHEUS_PORT=${PROMETHEUS_PORT:-9090}
export GRAFANA_PORT=${GRAFANA_PORT:-3000}

# Credentials with defaults
export RABBIT_USER=${RABBIT_USER:-guest}
export RABBIT_PASSWORD=${RABBIT_PASSWORD:-guest}
export REDIS_PASSWORD=${REDIS_PASSWORD:-}
export DB_USER=${DB_USER:-admin}
export DB_PASSWORD=${DB_PASSWORD:-root}
export DB_API=${DB_API:-hoplias}

# Service hosts (use localhost since everything is in one container)
export RABBIT_HOST=${RABBIT_HOST:-localhost}
export DB_HOST=${DB_HOST:-localhost}
export GRAYLOG_HOST=${GRAYLOG_HOST:-localhost}
export REDIS_URL=${REDIS_URL:-redis://localhost:6379}

# RabbitMQ aliases (for compatibility)
export HOST_MQ=${HOST_MQ:-$RABBIT_HOST}
export PORT_MQ=${PORT_MQ:-$RABBITMQ_PORT}
export USER_MQ=${USER_MQ:-$RABBIT_USER}
export PASSWORD_MQ=${PASSWORD_MQ:-$RABBIT_PASSWORD}

# FastAPI (api-service) specific variables
export ENV=${ENV:-development}
export FLASK_ENV=${FLASK_ENV:-development}
export APP_HOST=${APP_HOST:-0.0.0.0}
export APP_PORT=${APP_PORT:-$API_PORT}
export JWT_SIGNATURE_TOKEN=${JWT_SIGNATURE_TOKEN:-}
export JWT_SECRET_KEY=${JWT_SECRET_KEY:-}
export RPC_GATEWAY_KEY=${RPC_GATEWAY_KEY:-}
export CHATBOT_SECRET_KEY=${CHATBOT_SECRET_KEY:-}
export IP_HOST=${IP_HOST:-}
export HTTPS=${HTTPS:-true}
export ALLOWED_IP_HOST=${ALLOWED_IP_HOST:-}
export DESKTOP_MODE_AUTH=${DESKTOP_MODE_AUTH:-false}
export HOST_DOCUMENTS_DIR=${HOST_DOCUMENTS_DIR:-/app/api-service/local_storage}

# Database variables (mapping DB_PASSWORD to DB_PW for FastAPI compatibility)
export DB_PW=${DB_PW:-$DB_PASSWORD}
export DB_PORT=${DB_PORT:-$MONGODB_PORT}
export DB_NAME=${DB_NAME:-$DB_API}

# AWS Configuration
export AWS_REGION=${AWS_REGION:-}
export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-}
export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}

# Email Configuration
export MAIL_SERVER=${MAIL_SERVER:-}
export MAIL_PORT=${MAIL_PORT:-587}
export MAIL_USERNAME=${MAIL_USERNAME:-}
export MAIL_FROM=${MAIL_FROM:-}
export MAIL_PASSWORD=${MAIL_PASSWORD:-}

# Application URLs (use localhost for unified container)
export APP_PLATFORM_HOST=${APP_PLATFORM_HOST:-http://localhost:3001}
# Replace service names with localhost for unified container
BASE_URL_API_GATEWAY_VALUE=${BASE_URL_API_GATEWAY:-http://localhost:8001/v1/api}
BASE_URL_API_GATEWAY_VALUE=$(echo "$BASE_URL_API_GATEWAY_VALUE" | sed 's/hoplias-gateway/localhost/g')
export BASE_URL_API_GATEWAY=$BASE_URL_API_GATEWAY_VALUE

BASE_URL_API_AI_VALUE=${BASE_URL_API_AI:-http://localhost:5000/api/v1}
BASE_URL_API_AI_VALUE=$(echo "$BASE_URL_API_AI_VALUE" | sed 's/hoplias-api-ai/localhost/g')
export BASE_URL_API_AI=$BASE_URL_API_AI_VALUE

export REACT_APP_API_SERVICE=${REACT_APP_API_SERVICE:-}
export REACT_APP_AI_SERVICE=${REACT_APP_AI_SERVICE:-}
export AI_GPT_API_KEY=${AI_GPT_API_KEY:-}

# Construct DATABASE_URL for compatibility (if needed)
export DATABASE_URL=${DATABASE_URL:-mongodb://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_API}?authSource=admin}

# Google OAuth
export GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID:-}
export GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET:-}
export GOOGLE_REDIRECT_URI=${GOOGLE_REDIRECT_URI:-https://hoplias.com}

# GCP Configuration
export GCP_PROJECT_ID=${GCP_PROJECT_ID:-}
export GCP_PRIVATE_KEY_ID=${GCP_PRIVATE_KEY_ID:-}
export GCP_PRIVATE_KEY=${GCP_PRIVATE_KEY:-}
export GCP_CLIENT_EMAIL=${GCP_CLIENT_EMAIL:-}
export GCP_CLIENT_ID=${GCP_CLIENT_ID:-}
export GCP_CERT_URL=${GCP_CERT_URL:-}

# Other application variables
export TOKEN_EXPIRES_IN=${TOKEN_EXPIRES_IN:-1}
export RECOVER_CODE_EXPIRATION_DAYS=${RECOVER_CODE_EXPIRATION_DAYS:-7}
export MAX_CONCURRENT_IO_LOAD_IMAGES=${MAX_CONCURRENT_IO_LOAD_IMAGES:-20}
export SECRET_SQLBAK=${SECRET_SQLBAK:-}

# Graylog configuration
export GRAYLOG_ROOT_USERNAME=${GRAYLOG_ROOT_USERNAME:-admin}
export GRAYLOG_PORT_UDP=${GRAYLOG_PORT_UDP:-12201}
export GRAYLOG_PASSWORD=${GRAYLOG_PASSWORD:-}
export GRAYLOG_PASSWORD_SHA=${GRAYLOG_PASSWORD_SHA:-}
export GRAYLOG_HTTP_EXTERNAL_URI=${GRAYLOG_HTTP_EXTERNAL_URI:-http://localhost:9001/}
export GRAYLOG_HTTP_CORS_ALLOW_ORIGIN=${GRAYLOG_HTTP_CORS_ALLOW_ORIGIN:-}

# Grafana configuration
export GRAFANA_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
export GRAFANA_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}

# SonarQube (optional)
export SONAR_USER=${SONAR_USER:-admin}
export SONAR_PASSWORD=${SONAR_PASSWORD:-}
export SONAR_PROJECT_TOKEN=${SONAR_PROJECT_TOKEN:-}

# Function to wait for a service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=0

    log "Waiting for $service_name to be ready on $host:$port..."
    while [ $attempt -lt $max_attempts ]; do
        if nc -z $host $port 2>/dev/null; then
            log "$service_name is ready!"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    error "$service_name failed to start after $((max_attempts * 2)) seconds"
    return 1
}

# Function to start Redis - ESSENTIAL SERVICE
start_redis() {
    log "Starting Redis..."
    # Find redis-server binary
    REDIS_BIN=$(which redis-server 2>/dev/null || find /usr -name redis-server 2>/dev/null | head -1)
    
    if [ -z "$REDIS_BIN" ]; then
        error "Redis server not found. Redis is an ESSENTIAL service and must be installed."
        exit 1
    fi
    
    if [ -n "$REDIS_PASSWORD" ]; then
        $REDIS_BIN --port $REDIS_PORT --requirepass "$REDIS_PASSWORD" --daemonize yes --dir /data/redis
    else
        $REDIS_BIN --port $REDIS_PORT --daemonize yes --dir /data/redis
    fi
    wait_for_service localhost $REDIS_PORT "Redis" || (error "Redis failed to start" && exit 1)
}

# Function to start RabbitMQ - ESSENTIAL SERVICE
start_rabbitmq() {
    log "Starting RabbitMQ..."
    mkdir -p /data/rabbitmq /var/log/rabbitmq
    
    # Find rabbitmq-server binary
    RABBITMQ_BIN=$(which rabbitmq-server 2>/dev/null || find /usr -name rabbitmq-server 2>/dev/null | head -1)
    
    if [ -z "$RABBITMQ_BIN" ]; then
        error "RabbitMQ server not found. RabbitMQ is an ESSENTIAL service and must be installed."
        exit 1
    fi
    
    # Set RabbitMQ data directory
    export RABBITMQ_MNESIA_BASE=/data/rabbitmq
    
    # Start RabbitMQ in background
    $RABBITMQ_BIN -detached || true
    
    # Wait for RabbitMQ to be ready
    sleep 10
    
    # Wait for pid file
    timeout=30
    while [ $timeout -gt 0 ] && [ ! -f /var/lib/rabbitmq/mnesia/rabbit@$(hostname).pid ]; do
        sleep 1
        timeout=$((timeout - 1))
    done
    
    # Find rabbitmqctl binary
    RABBITMQCTL_BIN=$(which rabbitmqctl 2>/dev/null || find /usr -name rabbitmqctl 2>/dev/null | head -1)
    
    if [ -n "$RABBITMQCTL_BIN" ]; then
        # Configure user
        $RABBITMQCTL_BIN wait /var/lib/rabbitmq/mnesia/rabbit@$(hostname).pid 2>/dev/null || \
        $RABBITMQCTL_BIN wait /data/rabbitmq/rabbit@$(hostname).pid 2>/dev/null || sleep 5
        
        $RABBITMQCTL_BIN add_user $RABBIT_USER $RABBIT_PASSWORD 2>/dev/null || true
        $RABBITMQCTL_BIN set_user_tags $RABBIT_USER administrator 2>/dev/null || true
        $RABBITMQCTL_BIN set_permissions -p / $RABBIT_USER ".*" ".*" ".*" 2>/dev/null || true
    else
        warn "rabbitmqctl not found, skipping user configuration"
    fi
    
    wait_for_service localhost $RABBITMQ_PORT "RabbitMQ" || (error "RabbitMQ failed to start" && exit 1)
    log "RabbitMQ started"
}

# Function to start MongoDB - ESSENTIAL SERVICE
start_mongodb() {
    log "Starting MongoDB..."
    mkdir -p /data/mongodb /var/log/mongodb
    
    # Find mongod binary
    MONGOD_BIN=$(which mongod 2>/dev/null || find /usr -name mongod 2>/dev/null | head -1)
    
    if [ -z "$MONGOD_BIN" ]; then
        error "MongoDB server not found. MongoDB is an ESSENTIAL service and must be installed."
        exit 1
    fi
    
    # Start MongoDB without auth first
    $MONGOD_BIN --bind_ip_all --port $MONGODB_PORT --dbpath /data/mongodb --fork --logpath /var/log/mongodb/mongod.log
    
    # Wait for MongoDB to start
    sleep 10
    
    # Find mongo/mongosh binary
    MONGO_CLIENT=$(which mongosh 2>/dev/null || which mongo 2>/dev/null || find /usr -name mongosh 2>/dev/null | head -1 || find /usr -name mongo 2>/dev/null | head -1)
    
    if [ -n "$MONGO_CLIENT" ]; then
        # Create admin user if it doesn't exist
        $MONGO_CLIENT --quiet --eval "db.getUser('$DB_USER')" admin 2>/dev/null || \
        $MONGO_CLIENT --quiet admin --eval "db.createUser({user: '$DB_USER', pwd: '$DB_PASSWORD', roles: ['root']})" 2>/dev/null || true
    else
        warn "MongoDB client not found, skipping user creation"
    fi
    
    # Shutdown and restart with auth
    $MONGOD_BIN --shutdown --dbpath /data/mongodb 2>/dev/null || true
    
    sleep 2
    
    # Start with authentication
    $MONGOD_BIN --bind_ip_all --port $MONGODB_PORT --dbpath /data/mongodb --auth --fork --logpath /var/log/mongodb/mongod.log
    
    wait_for_service localhost $MONGODB_PORT "MongoDB" || (error "MongoDB failed to start" && exit 1)
}

# Function to start Elasticsearch - ESSENTIAL SERVICE
start_elasticsearch() {
    log "Starting Elasticsearch..."
    mkdir -p /data/elasticsearch
    chown -R elasticsearch:elasticsearch /data/elasticsearch 2>/dev/null || true
    
    # Find Elasticsearch binary
    ES_BIN=$(find /usr/share/elasticsearch -name elasticsearch 2>/dev/null | head -1)
    
    if [ -z "$ES_BIN" ]; then
        error "Elasticsearch not found. Elasticsearch is an ESSENTIAL service and must be installed."
        exit 1
    fi
    
    # Set JVM options for minimal memory usage
    export ES_JAVA_OPTS="-Xms512m -Xmx512m"
    # Start Elasticsearch in background
    $ES_BIN -d -p /var/run/elasticsearch/elasticsearch.pid || \
    su - elasticsearch -c "$ES_BIN -d -p /var/run/elasticsearch/elasticsearch.pid" || \
    (error "Failed to start Elasticsearch" && exit 1)
    sleep 10
    wait_for_service localhost $ELASTICSEARCH_PORT "Elasticsearch" || (error "Elasticsearch failed to start" && exit 1)
}

# Function to start Graylog - ESSENTIAL SERVICE
start_graylog() {
    log "Starting Graylog..."
    # Graylog requires MongoDB and Elasticsearch to be running first
    wait_for_service localhost $MONGODB_PORT "MongoDB" || (error "MongoDB must be running for Graylog" && exit 1)
    wait_for_service localhost $ELASTICSEARCH_PORT "Elasticsearch" || (error "Elasticsearch must be running for Graylog" && exit 1)
    
    # Find Graylog binary
    GRAYLOG_BIN=$(find /usr/share/graylog-server -name graylog-server 2>/dev/null | head -1)
    
    if [ -z "$GRAYLOG_BIN" ]; then
        error "Graylog not found. Graylog is an ESSENTIAL service and must be installed."
        exit 1
    fi
    
    # Set Graylog environment variables
    export GRAYLOG_HTTP_BIND_ADDRESS=0.0.0.0:$GRAYLOG_PORT
    export GRAYLOG_HTTP_EXTERNAL_URI=${GRAYLOG_HTTP_EXTERNAL_URI:-http://localhost:$GRAYLOG_PORT/}
    
    # Start Graylog
    $GRAYLOG_BIN -d || \
    su - graylog -c "$GRAYLOG_BIN -d" || \
    (error "Failed to start Graylog" && exit 1)
    sleep 15
    wait_for_service localhost $GRAYLOG_PORT "Graylog" || (error "Graylog failed to start" && exit 1)
    log "Graylog started"
}

# Function to start Prometheus
start_prometheus() {
    log "Starting Prometheus..."
    /opt/prometheus/prometheus --config.file=/app/prometheus.yml --storage.tsdb.path=/data/prometheus --web.listen-address=0.0.0.0:$PROMETHEUS_PORT &
    wait_for_service localhost $PROMETHEUS_PORT "Prometheus"
}

# Function to start Grafana
start_grafana() {
    log "Starting Grafana..."
    # Configure Grafana environment variables
    export GF_SERVER_HTTP_PORT=$GRAFANA_PORT
    export GF_SECURITY_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
    export GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-admin}
    
    # Start Grafana
    if [ -f /usr/sbin/grafana-server ]; then
        /usr/sbin/grafana-server --config=/etc/grafana/grafana.ini --homepath=/usr/share/grafana --pidfile=/var/run/grafana-server.pid &
    elif [ -f /usr/bin/grafana-server ]; then
        /usr/bin/grafana-server --config=/etc/grafana/grafana.ini --homepath=/usr/share/grafana --pidfile=/var/run/grafana-server.pid &
    fi
    sleep 5
    wait_for_service localhost $GRAFANA_PORT "Grafana"
}

# Function to configure Nginx
configure_nginx() {
    log "Configuring Nginx..."
    # Copy nginx configuration
    cp /app/config/nginx-less.conf /etc/nginx/conf.d/default.conf
    
    # Update ports in nginx config if needed
    sed -i "s/listen 80/listen $NGINX_PORT/g" /etc/nginx/conf.d/default.conf || true
    
    # Update upstream servers to use localhost
    sed -i "s/hoplias-api-service:8005/localhost:$API_PORT/g" /etc/nginx/conf.d/default.conf || true
    sed -i "s/grafana:3000/localhost:$GRAFANA_PORT/g" /etc/nginx/conf.d/default.conf || true
    sed -i "s/graylog:9001/localhost:$GRAYLOG_PORT/g" /etc/nginx/conf.d/default.conf || true
    sed -i "s/portainer:9000/localhost:9000/g" /etc/nginx/conf.d/default.conf || true
    sed -i "s/hoplias-rabbitmq:15672/localhost:$RABBITMQ_MANAGEMENT_PORT/g" /etc/nginx/conf.d/default.conf || true
}

# Function to start Nginx
start_nginx() {
    log "Starting Nginx..."
    configure_nginx
    nginx -g "daemon off;" &
    log "Nginx started"
}

# Main initialization
main() {
    log "Starting Hoplias Unified Container..."
    
    # Create necessary directories
    mkdir -p /data/redis /data/rabbitmq /data/mongodb /data/elasticsearch /data/prometheus /data/grafana
    mkdir -p /var/log/{redis,rabbitmq,mongodb,nginx,elasticsearch,graylog,prometheus,grafana}
    
    # Start infrastructure services in order
    # ESSENTIAL services - must start successfully
    start_redis
    start_rabbitmq
    start_mongodb
    start_elasticsearch
    start_graylog
    
    # Optional monitoring services
    start_prometheus || warn "Prometheus failed to start, continuing..."
    start_grafana || warn "Grafana failed to start, continuing..."
    
    # Reverse proxy last
    start_nginx
    
    # Wait a bit for all services to stabilize
    log "Waiting for services to stabilize..."
    sleep 10
    
    # Start supervisor to manage Python services
    log "Starting Supervisor for Python services..."
    exec /usr/local/bin/supervisord -c /app/supervisor/supervisord.conf
}

# Handle shutdown signals
trap 'log "Shutting down..."; killall supervisord; exit 0' SIGTERM SIGINT

# Run main function
main

