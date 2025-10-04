# NetSentry - Docker Quick Start

Get NetSentry running in Docker in 3 commands! 🐳

---

## 🚀 Super Quick Start

```bash
cd /Users/puneetgani/Documents/hackathon/netsentry

# Build and start everything
docker-compose up --build
```

**That's it!** Wait 30-60 seconds for builds to complete.

Access:
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

Press `Ctrl+C` to stop.

---

## 📋 Step-by-Step

### 1. Verify Docker is Installed

```bash
docker --version
docker-compose --version
```

If not installed: https://docs.docker.com/get-docker/

### 2. Build Images (Optional)

```bash
# Use the build script
./build-docker.sh

# Or build manually
docker-compose build
```

### 3. Start Services

```bash
# Start in foreground (see logs)
docker-compose up

# Or start in background
docker-compose up -d
```

### 4. Test the Application

**Browser:**
1. Open http://localhost:3000
2. Click "Example: Suspicious IP"
3. Click "Analyze Traffic"
4. See alert appear! 🎉

**cURL:**
```bash
curl http://localhost:8000/health
```

### 5. Stop Services

```bash
# If running in foreground
Press Ctrl+C

# If running in background
docker-compose down
```

---

## 🔍 View Logs

```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

---

## 🛠️ Troubleshooting

### Port Already in Use

```bash
# Stop local development servers first
./stop-all.sh

# Or change ports in docker-compose.yml
ports:
  - "8001:8000"  # Backend
  - "3001:3000"  # Frontend
```

### Build Failed

```bash
# Clean and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Can't Connect to API

```bash
# Check backend is running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Verify health
curl http://localhost:8000/health
```

---

## 📊 What's Running?

```bash
# List containers
docker-compose ps

# Check resource usage
docker stats

# See images
docker images | grep netsentry
```

---

## 🧹 Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove images too
docker-compose down --rmi all

# Remove everything (including volumes)
docker-compose down -v --rmi all
```

---

## 🎯 Common Commands

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Stop
docker-compose stop

# Restart
docker-compose restart

# Remove
docker-compose down

# Logs
docker-compose logs -f

# Shell access
docker exec -it netsentry-backend /bin/bash
docker exec -it netsentry-frontend /bin/sh
```

---

## ✅ Testing Checklist

After starting:

- [ ] `docker-compose ps` shows 2 running containers
- [ ] http://localhost:8000/health returns `{"status":"ok"}`
- [ ] http://localhost:3000 loads dashboard
- [ ] Health indicator shows "Online" (green)
- [ ] Can submit analysis via frontend
- [ ] Alerts appear in "View Alerts" tab

---

## 🚀 Production Tips

### Use Specific Tags

```bash
docker build -t netsentry-backend:v1.0.0 .
```

### Set Environment Variables

Create `.env` file:
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Deploy to Cloud

```bash
# AWS ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag netsentry-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/netsentry-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/netsentry-backend:latest
```

---

## 📚 More Info

See `DOCKER_GUIDE.md` for comprehensive documentation.

---

**🎉 You're running NetSentry in Docker!**

Need help? Check logs: `docker-compose logs -f`

