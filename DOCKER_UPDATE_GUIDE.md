# Docker Images Update Guide

## Overview

This guide explains how to build and run the updated NetSentry Docker images with ML support.

## What's Included

### Backend Image
- ✅ FastAPI REST API
- ✅ ML Random Forest models (Binary & Multi-class)
- ✅ ML dependencies (pandas, numpy, scikit-learn, joblib)
- ✅ Network analysis (no nmap dependency)
- ✅ Rule-based detection
- ✅ Alert management

### Frontend Image
- ✅ Next.js dashboard
- ✅ ML Prediction interface
- ✅ Network scanner with charts (recharts)
- ✅ Alert visualization
- ✅ Responsive design

## Prerequisites

- Docker: `>=20.10.0`
- Docker Compose: `>=2.0.0`
- Trained ML models (optional, but recommended)

## Quick Start

### Option 1: Docker Compose (Recommended)

Build and run both services:

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Using Build Script

```bash
# Make script executable (first time only)
chmod +x build-docker.sh

# Build both images
./build-docker.sh

# Run with docker-compose
docker-compose up
```

### Option 3: Manual Build

Build images separately:

```bash
# Backend
docker build -t netsentry-backend:latest .

# Frontend
cd frontend
docker build -t netsentry-frontend:latest .
cd ..

# Run
docker-compose up
```

## Training ML Models

**IMPORTANT:** The ML models need to be trained before full functionality is available.

### Option 1: Train Before Building (Recommended)

```bash
# 1. Train models using the notebook
cd modelBuilding
jupyter notebook random_forest_intrusion_detection.ipynb
# Run all cells to train and save models

# 2. Verify models are created
ls -la modelBuilding/models/
# Should see:
# - rf_binary_classifier.pkl
# - rf_multiclass_classifier.pkl
# - label_encoders.pkl
# - feature_columns.pkl
# - attack_mapping.pkl

# 3. Build Docker images (models will be included)
cd ..
docker-compose up --build
```

### Option 2: Train After Starting Container

If you start the container without models:

```bash
# Start services
docker-compose up -d

# Train models locally
cd modelBuilding
jupyter notebook random_forest_intrusion_detection.ipynb
# Run all cells

# Copy models to running container
docker cp modelBuilding/models netsentry-backend:/app/modelBuilding/

# Restart backend to load models
docker-compose restart backend
```

## Accessing Services

After starting:

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

## Verifying ML Models

Check if ML models are loaded:

```bash
# Method 1: Via API
curl http://localhost:8000/ml/status

# Expected response:
{
  "models_loaded": true,
  "binary_model_available": true,
  "multiclass_model_available": true,
  "features_count": 44,
  "message": "ML models ready"
}

# Method 2: Via Docker logs
docker-compose logs backend | grep "ML models"
# Should see: "✓ ML models loaded successfully"
```

## Environment Variables

### Backend

```yaml
PYTHONUNBUFFERED=1  # Better logging
```

### Frontend

```yaml
NODE_ENV=production
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Ports

| Service | Port | Purpose |
|---------|------|---------|
| Backend | 8000 | REST API |
| Frontend | 3000 | Web Dashboard |

## Health Checks

### Backend

```bash
curl http://localhost:8000/health
```

### Container Health

```bash
docker-compose ps
# Both services should show "healthy"
```

## Troubleshooting

### ML Models Not Loading

**Symptom:** `/ml/status` shows `models_loaded: false`

**Solution:**
```bash
# Check if models exist in container
docker exec netsentry-backend ls -la modelBuilding/models/

# If missing, train locally and copy
cd modelBuilding
jupyter notebook random_forest_intrusion_detection.ipynb
# Run all cells

docker cp modelBuilding/models netsentry-backend:/app/modelBuilding/
docker-compose restart backend
```

### Frontend Build Fails

**Symptom:** `npm install` or `npm run build` errors

**Solution:**
```bash
# Clean npm cache
cd frontend
rm -rf node_modules package-lock.json
npm install
cd ..

# Rebuild
docker-compose build frontend --no-cache
```

### Port Already in Use

**Symptom:** `port is already allocated`

**Solution:**
```bash
# Option 1: Stop conflicting service
lsof -ti:8000 | xargs kill
lsof -ti:3000 | xargs kill

# Option 2: Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Backend
  - "3001:3000"  # Frontend
```

### Backend Can't Connect to Network

**Symptom:** Network scan fails

**Solution:**
```bash
# Run with host network (Linux only)
docker run --network=host netsentry-backend

# Or use docker-compose with host network
# Edit docker-compose.yml:
network_mode: "host"
```

## Updating Images

### Pull Latest Code

```bash
git pull origin main
```

### Rebuild

```bash
# Rebuild everything
docker-compose build --no-cache

# Or rebuild specific service
docker-compose build --no-cache backend
docker-compose build --no-cache frontend
```

### Clean Up Old Images

```bash
# Remove old images
docker image prune -a

# Or specifically
docker rmi netsentry-backend:latest
docker rmi netsentry-frontend:latest
```

## Production Deployment

### Security Considerations

1. **Change default ports** in production
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** with reverse proxy (nginx)
4. **Set proper CORS origins** in backend
5. **Use Docker secrets** for API keys

### Example Production Setup

```bash
# Use docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d
```

### Resource Limits

Add to docker-compose.yml:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
          
  frontend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Image Sizes

Expected sizes:
- Backend: ~800MB (with ML libraries)
- Frontend: ~200MB (optimized Next.js)

## Testing

### Test Backend

```bash
docker exec netsentry-backend curl http://localhost:8000/health
docker exec netsentry-backend curl http://localhost:8000/ml/status
```

### Test Frontend

```bash
curl http://localhost:3000
```

### Run Integration Test

```bash
# From host
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"192.168.1.100","dst_ip":"8.8.8.8","protocol":"TCP"}'
```

## Logs

### View All Logs

```bash
docker-compose logs -f
```

### View Specific Service

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Save Logs

```bash
docker-compose logs > netsentry-logs.txt
```

## Stopping Services

```bash
# Stop services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v

# Stop and remove everything including images
docker-compose down --rmi all
```

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify models: `curl http://localhost:8000/ml/status`
3. Check health: `docker-compose ps`
4. Review documentation: `/docs` endpoint

## Summary

✅ Updated Docker images include:
- ML Random Forest models
- Enhanced network scanner
- Interactive charts and graphs
- Removed nmap dependency
- All latest features

⚠️ Remember to train ML models for full functionality!

