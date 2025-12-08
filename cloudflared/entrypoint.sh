#!/bin/sh
# Entrypoint script for cloudflared
# Generates config.yml with token from environment variable

set -e

# Create config file with token
echo "tunnel: ${CLOUDFLARE_TUNNEL_TOKEN}" > /tmp/config.yml
echo "" >> /tmp/config.yml

# Append ingress rules from mounted config
cat /etc/cloudflared/config.yml >> /tmp/config.yml

# Run cloudflared with the generated config
exec tunnel --no-autoupdate run --config /tmp/config.yml

