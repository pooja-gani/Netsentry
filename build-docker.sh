#!/bin/bash

echo "═══════════════════════════════════════════════════════"
echo "  NetSentry - Docker Build Script"
echo "═══════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker found:${NC} $(docker --version)"
echo -e "${GREEN}✓ Docker Compose found:${NC} $(docker-compose --version)"
echo ""

# Build images
echo "═══════════════════════════════════════════════════════"
echo "  Building Docker Images..."
echo "═══════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}→ Building backend image...${NC}"
docker build -t netsentry-backend:latest .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend image built successfully${NC}"
else
    echo -e "${RED}✗ Backend build failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}→ Building frontend image...${NC}"
docker build -t netsentry-frontend:latest ./frontend
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend image built successfully${NC}"
else
    echo -e "${RED}✗ Frontend build failed${NC}"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  ✓ Build Complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Docker images created:"
docker images | grep netsentry
echo ""
echo "Next steps:"
echo "  1. Run with Docker Compose: docker-compose up"
echo "  2. Or run manually:"
echo "     - Backend:  docker run -p 8000:8000 netsentry-backend:latest"
echo "     - Frontend: docker run -p 3000:3000 netsentry-frontend:latest"
echo ""

