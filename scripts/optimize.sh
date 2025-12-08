#!/bin/bash
# Post-installation optimization script

echo "Running post-installation optimizations..."

# Remove unnecessary packages
apt-get autoremove -y
apt-get clean

# Remove build dependencies if any
rm -rf /var/lib/apt/lists/*
rm -rf /tmp/*
rm -rf /var/tmp/*

# Remove Python cache
find /app -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find /app -type f -name "*.pyc" -delete 2>/dev/null || true
find /app -type f -name "*.pyo" -delete 2>/dev/null || true

# Remove documentation
find /usr/share/doc -type f -delete 2>/dev/null || true
find /usr/share/man -type f -delete 2>/dev/null || true

# Remove locale files (keep only en_US)
find /usr/share/locale -mindepth 1 -maxdepth 1 ! -name 'en_US*' -exec rm -r {} + 2>/dev/null || true

echo "Optimization complete"

