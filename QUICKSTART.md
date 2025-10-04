# NetSentry - Quick Start Guide

## 🚀 Stage 1: Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd /Users/puneetgani/Documents/hackathon/netsentry
pip install -r requirements.txt
```

### Step 2: Start the Server
```bash
python app.py
```

Server will start at: `http://localhost:8000`

### Step 3: Test the API

#### Option A: Run automated test suite
```bash
./test_api.sh
```

#### Option B: Manual testing with curl

**Test 1: Health Check**
```bash
curl http://localhost:8000/health
```

**Test 2: Analyze suspicious IP**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.100.100",
    "dst_ip": "10.0.0.1",
    "protocol": "TCP",
    "payload": "Suspicious traffic"
  }'
```

**Test 3: View all alerts**
```bash
curl http://localhost:8000/alerts
```

---

## 📊 Interactive Documentation

Open in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints interactively from the browser!

---

## 🎯 What's Working

✅ **POST /analyze** - Analyzes network logs and detects:
  - Suspicious source IPs
  - Excessive login attempts (5+ from same IP)
  - Suspicious DNS queries

✅ **GET /alerts** - Retrieves all detected alerts with filtering

✅ **GET /health** - Health check endpoint

✅ **GET /stats** - System statistics

---

## 📝 Sample Test Scenarios

### Scenario 1: Normal Traffic (No Alert)
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.1.10",
    "dst_ip": "8.8.8.8",
    "protocol": "TCP",
    "payload": "Normal HTTP request"
  }'
```
**Expected**: `"status": "clean"`

### Scenario 2: Malicious DNS Query
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.1.25",
    "dst_ip": "8.8.8.8",
    "protocol": "DNS",
    "payload": "malware-botnet.tk"
  }'
```
**Expected**: `"severity": "HIGH"`, `"alert_type": "SUSPICIOUS_DNS_QUERY"`

### Scenario 3: Brute Force Attack
Run this 5 times to trigger alert:
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "203.0.114.50",
    "dst_ip": "192.168.1.100",
    "protocol": "HTTP",
    "payload": "POST /login username=admin&password=guess"
  }'
```
**Expected** (after 5th attempt): `"alert_type": "EXCESSIVE_LOGIN_ATTEMPTS"`

---

## 🔧 Troubleshooting

### "Port 8000 already in use"
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>

# Or use a different port
uvicorn app:app --port 8001
```

### "Module not found"
```bash
# Make sure you're in the right directory
cd /Users/puneetgani/Documents/hackathon/netsentry

# Reinstall dependencies
pip install -r requirements.txt
```

---

## ✅ Stage 1 Checklist

Before moving to Stage 2, verify:

- [ ] Server starts without errors
- [ ] `/health` endpoint returns `"status": "ok"`
- [ ] `/analyze` detects suspicious IPs
- [ ] `/analyze` detects excessive login attempts
- [ ] `/analyze` detects suspicious DNS queries
- [ ] `/alerts` returns stored alerts
- [ ] Interactive docs work at `/docs`

---

## 🎉 Ready for Stage 2?

Once you've tested everything and it works, confirm with me and we'll proceed to:

**Stage 2: Dockerization**
- Create Dockerfile
- Build Docker image
- Run containerized service
- Test endpoints inside container

---

**Questions or issues?** Let me know and I'll help debug! 🚀

