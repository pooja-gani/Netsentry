# NetSentry - Docker Deployment Guide

Complete guide for running NetSentry in Docker containers.

---

## 🐳 Prerequisites

- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)

**Check installations:**
```bash
docker --version
docker-compose --version
```

**Install Docker**: https://docs.docker.com/get-docker/

---

## 🚀 Quick Start (Recommended)

### Option 1: Using Docker Compose (Easiest)

```bash
cd /Users/puneetgani/Documents/hackathon/netsentry

# Build and start all services
docker-compose up --build
```

That's it! The application will be running at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Build Script + Docker Compose

```bash
# Build images
./build-docker.sh

# Start services
docker-compose up
```

### Option 3: Manual Build and Run

See "Manual Docker Commands" section below.

---

## 📦 What Gets Built

### Backend Container
- **Base Image**: Python 3.10 slim
- **Size**: ~200MB
- **Includes**: FastAPI, Uvicorn, all dependencies
- **Port**: 8000
- **Health Check**: Automatic every 30s

### Frontend Container
- **Base Image**: Node 18 Alpine
- **Size**: ~150MB (multi-stage build)
- **Includes**: Next.js production build
- **Port**: 3000
- **Optimized**: Standalone output, non-root user

---

## 🔧 Docker Compose Configuration

The `docker-compose.yml` orchestrates both services:

```yaml
services:
  backend:  # FastAPI on port 8000
  frontend: # Next.js on port 3000
```

**Features:**
- ✅ Automatic networking between containers
- ✅ Health checks for backend
- ✅ Frontend waits for backend to be healthy
- ✅ Auto-restart on failure
- ✅ Proper environment variables

---

## 📋 Common Commands

### Start Services

```bash
# Build and start (detached mode)
docker-compose up -d --build

# Start with logs (foreground)
docker-compose up --build

# Start without rebuilding
docker-compose up -d
```

### Stop Services

```bash
# Stop containers (keeps data)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop, remove, and clean volumes
docker-compose down -v
```

### View Logs

```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Last 50 lines
docker-compose logs --tail=50 -f
```

### Check Status

```bash
# List running containers
docker-compose ps

# Check resource usage
docker stats

# Inspect network
docker network ls
docker network inspect netsentry_netsentry-network
```

### Rebuild

```bash
# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Rebuild everything
docker-compose build --no-cache
```

---

## 🧪 Testing the Dockerized Application

### 1. Health Check

```bash
# Backend health
curl http://localhost:8000/health

# Expected: {"status":"ok", ...}
```

### 2. Test API

```bash
# Analyze suspicious IP
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.100.100",
    "dst_ip": "10.0.0.1",
    "protocol": "TCP",
    "payload": "test"
  }'
```

### 3. Test Frontend

Open browser: http://localhost:3000
- Click "Example: Suspicious IP"
- Click "Analyze Traffic"
- Verify alert appears

---

## 🛠️ Manual Docker Commands

If you prefer not to use Docker Compose:

### Build Images

```bash
# Build backend
docker build -t netsentry-backend:latest .

# Build frontend
docker build -t netsentry-frontend:latest ./frontend
```

### Run Containers

```bash
# Create network
docker network create netsentry-net

# Run backend
docker run -d \
  --name netsentry-backend \
  --network netsentry-net \
  -p 8000:8000 \
  netsentry-backend:latest

# Run frontend
docker run -d \
  --name netsentry-frontend \
  --network netsentry-net \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  netsentry-frontend:latest
```

### Stop Containers

```bash
docker stop netsentry-backend netsentry-frontend
docker rm netsentry-backend netsentry-frontend
```

---

## 🔍 Debugging

### Container Not Starting

```bash
# Check logs
docker logs netsentry-backend
docker logs netsentry-frontend

# Check if ports are in use
lsof -i :8000
lsof -i :3000

# Inspect container
docker inspect netsentry-backend
```

### Backend/Frontend Can't Connect

```bash
# Check network
docker network inspect netsentry_netsentry-network

# Verify containers are on same network
docker-compose ps
```

### Rebuild from Scratch

```bash
# Stop everything
docker-compose down

# Remove images
docker rmi netsentry-backend:latest netsentry-frontend:latest

# Clear cache and rebuild
docker-compose build --no-cache
docker-compose up
```

### Enter Container Shell

```bash
# Backend
docker exec -it netsentry-backend /bin/bash

# Frontend
docker exec -it netsentry-frontend /bin/sh
```

---

## 📊 Resource Usage

Typical resource requirements:

**Backend Container:**
- CPU: ~0.5%
- Memory: ~50-100 MB
- Disk: ~200 MB

**Frontend Container:**
- CPU: ~0.3%
- Memory: ~30-50 MB
- Disk: ~150 MB

**Total:** ~400 MB disk, ~150 MB RAM

---

## 🌐 Production Deployment

### Environment Variables

Create `.env` file:

```bash
# Backend
BACKEND_PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NODE_ENV=production
```

Update `docker-compose.yml`:

```yaml
services:
  backend:
    env_file: .env
  frontend:
    env_file: .env
```

### CORS Configuration

For production, update `app.py` CORS settings:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",
    ],
    ...
)
```

### Use Docker Swarm or Kubernetes

For production scale:

**Docker Swarm:**
```bash
docker swarm init
docker stack deploy -c docker-compose.yml netsentry
```

**Kubernetes:**
```bash
# Convert compose to k8s
kompose convert -f docker-compose.yml

# Deploy
kubectl apply -f .
```

---

## 📦 Push to Docker Hub (Optional)

Share your images:

```bash
# Login
docker login

# Tag images
docker tag netsentry-backend:latest yourusername/netsentry-backend:latest
docker tag netsentry-frontend:latest yourusername/netsentry-frontend:latest

# Push
docker push yourusername/netsentry-backend:latest
docker push yourusername/netsentry-frontend:latest
```

---

## 🔐 Security Best Practices

### For Production:

1. **Use secrets for sensitive data:**
   ```bash
   docker secret create api_key ./api_key.txt
   ```

2. **Run as non-root user** (already done in frontend)

3. **Scan images for vulnerabilities:**
   ```bash
   docker scan netsentry-backend:latest
   ```

4. **Use multi-stage builds** (already implemented)

5. **Keep base images updated:**
   ```bash
   docker pull python:3.10-slim
   docker pull node:18-alpine
   ```

---

## 🚀 CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build images
        run: docker-compose build
      - name: Push to registry
        run: |
          docker login -u ${{ secrets.DOCKER_USERNAME }} -p ${{ secrets.DOCKER_PASSWORD }}
          docker-compose push
```

---

## 📝 Dockerfile Details

### Backend Dockerfile
- Uses Python 3.10 slim base
- Installs dependencies via pip
- Runs uvicorn on port 8000
- Health check endpoint configured

### Frontend Dockerfile
- Multi-stage build (deps → builder → runner)
- Node 18 Alpine for small size
- Standalone output for production
- Non-root user for security

---

## ✅ Docker Checklist

Before deploying:

- [ ] Docker and Docker Compose installed
- [ ] Images build successfully
- [ ] Containers start without errors
- [ ] Backend health check passes
- [ ] Frontend can reach backend
- [ ] All endpoints work via frontend
- [ ] Logs show no errors
- [ ] Resource usage acceptable

---

## 🎉 Next Steps

### Stage 3: Cloud Integration

Once Docker is working:
- Deploy to AWS ECS/Fargate
- Add S3 for alert storage
- CloudWatch for monitoring
- Lambda for notifications
- API Gateway for routing

---

## 📚 Resources

- **Docker Docs**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **FastAPI in Docker**: https://fastapi.tiangolo.com/deployment/docker/
- **Next.js Docker**: https://nextjs.org/docs/deployment#docker-image

---

**🐳 Your NetSentry is now Dockerized!**

Run: `docker-compose up --build`

Visit: http://localhost:3000

