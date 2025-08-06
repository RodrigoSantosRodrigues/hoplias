FROM node:20-bullseye AS builder

# Argument for build target
ARG BUILD_TARGET=linux

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    libgtk-3-0 \
    libnotify4 \
    libnss3 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    libatspi2.0-0 \
    libuuid1 \
    libsecret-1-0 \
    && rm -rf /var/lib/apt/lists/*

# Platform-specific build tools
RUN if [ "$BUILD_TARGET" = "mac" ]; then \
    apt-get update && \
    apt-get install -y \
    build-essential \
    python3 \
    git \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*; \
    elif [ "$BUILD_TARGET" = "win" ]; then \
    apt-get update && \
    apt-get install -y \
    wine \
    && rm -rf /var/lib/apt/lists/*; \
    fi

WORKDIR /app

# Cache dependencies
COPY package.json yarn.lock ./

RUN yarn install --frozen-lockfile --ignore-optional

# Copy application code
COPY . .

# Build application with dynamic target
RUN yarn build:${BUILD_TARGET}

# Final stage
FROM node:20-bullseye-slim

WORKDIR /app
COPY --from=builder /app/dist ./dist

VOLUME /output

CMD ["sh", "-c", "cp -r dist/* /output/"]
