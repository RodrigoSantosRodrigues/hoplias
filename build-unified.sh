#!/bin/bash
# Build script for unified Hoplias image

set -e

IMAGE_NAME=${IMAGE_NAME:-hoplias-unified}
IMAGE_TAG=${IMAGE_TAG:-latest}
DOCKERFILE=${DOCKERFILE:-Dockerfile.unified-optimized}

echo "Building Hoplias Unified Image..."
echo "Image: $IMAGE_NAME:$IMAGE_TAG"
echo "Dockerfile: $DOCKERFILE"
echo ""

# Build the image
docker build -f $DOCKERFILE -t $IMAGE_NAME:$IMAGE_TAG .

echo ""
echo "Build completed successfully!"
echo ""
echo "Image size:"
docker images $IMAGE_NAME:$IMAGE_TAG --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ""
echo "To run the image:"
echo "  docker run -d --name hoplias -p 8001:8001 -p 8080:8080 $IMAGE_NAME:$IMAGE_TAG"
echo ""
echo "To test the image:"
echo "  cd tests && ./test-unified-image.sh"

