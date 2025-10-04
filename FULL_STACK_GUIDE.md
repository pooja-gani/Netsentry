# NetSentry - Full Stack Setup Guide

Complete guide to running the **Backend API** + **Frontend Dashboard** together.

---

## 🚀 Quick Start (Both Backend + Frontend)

### Step 1: Install Backend Dependencies

```bash
cd /Users/puneetgani/Documents/hackathon/netsentry
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies

```bash
cd /Users/puneetgani/Documents/hackathon/netsentry/frontend
npm install
```

### Step 3: Start Backend (Terminal 1)

```bash
cd /Users/puneetgani/Documents/hackathon/netsentry
python app.py
```

✅ Backend running at: **http://localhost:8000**

### Step 4: Start Frontend (Terminal 2)

```bash
cd /Users/puneetgani/Documents/hackathon/netsentry/frontend
npm run dev
```

✅ Frontend running at: **http://localhost:3000**

### Step 5: Open Dashboard

Open your browser: **http://localhost:3000**

---

## 📋 Pre-Flight Checklist

Before starting, ensure you have:

- ✅ Python 3.10+ installed (`python --version`)
- ✅ Node.js 18+ installed (`node --version`)
- ✅ npm installed (`npm --version`)
- ✅ Ports 8000 and 3000 available

---

## 🎯 Testing the Full Stack

### Test 1: Backend Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-03T...",
  "version": "1.0.0"
}
```

### Test 2: Frontend Dashboard

1. Open http://localhost:3000
2. Check that health indicator shows "Online" (green badge)
3. Verify statistics cards show "0" for new installation

### Test 3: Submit Analysis via Frontend

1. Click "Analyze Traffic" tab
2. Click "Example: Suspicious IP" button
3. Click "Analyze Traffic" button
4. See alert appear in results
5. Switch to "View Alerts" tab
6. Verify alert appears in table

### Test 4: Auto-Refresh

1. Keep frontend open
2. Submit alert via curl (in terminal):
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"192.168.100.100","dst_ip":"10.0.0.1","protocol":"TCP","payload":"test"}'
```
3. Watch frontend auto-update within 30 seconds

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      Browser                             │
│              http://localhost:3000                       │
│  ┌────────────────────────────────────────────────┐    │
│  │         NetSentry Dashboard (Next.js)           │    │
│  │  - View Statistics                              │    │
│  │  - Analyze Traffic                              │    │
│  │  - View Alerts                                  │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                         │
                         │ REST API (HTTP)
                         ↓
┌─────────────────────────────────────────────────────────┐
│              http://localhost:8000                       │
│  ┌────────────────────────────────────────────────┐    │
│  │       NetSentry API (FastAPI)                   │    │
│  │  - POST /analyze                                │    │
│  │  - GET /alerts                                  │    │
│  │  - GET /health                                  │    │
│  │  - GET /stats                                   │    │
│  └────────────────────────────────────────────────┘    │
│              ↓                                           │
│  ┌────────────────────────────────────────────────┐    │
│  │    Detection Rules Engine                       │    │
│  │  - Suspicious IP Detection                      │    │
│  │  - Excessive Login Attempts                     │    │
│  │  - Suspicious DNS Queries                       │    │
│  └────────────────────────────────────────────────┘    │
│              ↓                                           │
│  ┌────────────────────────────────────────────────┐    │
│  │    In-Memory Storage (Stage 1)                  │    │
│  │  - Alerts Database                              │    │
│  │  - Login Attempts Tracker                       │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
netsentry/
├── app.py                      # FastAPI backend
├── requirements.txt            # Python dependencies
├── test_api.sh                 # Backend test script
├── README.md                   # Backend documentation
├── QUICKSTART.md              # Quick start guide
├── FULL_STACK_GUIDE.md        # This file
│
└── frontend/
    ├── app/
    │   ├── page.tsx           # Main dashboard page
    │   ├── layout.tsx         # Root layout
    │   └── globals.css        # Global styles
    ├── components/
    │   ├── ui/                # shadcn/ui components
    │   ├── stats-cards.tsx    # Statistics display
    │   ├── alerts-table.tsx   # Alerts table
    │   ├── log-analyzer.tsx   # Traffic analyzer form
    │   └── health-indicator.tsx # Health status
    ├── lib/
    │   └── api.ts             # API client
    ├── package.json           # Node dependencies
    ├── .env.local             # Environment config
    └── README.md              # Frontend documentation
```

---

## 🔧 Configuration

### Backend Configuration

**File**: `app.py` (lines 365-371)

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Change port:
```python
uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Frontend Configuration

**File**: `frontend/.env.local`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

If you change the backend port, update this file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

---

## 🧪 End-to-End Testing Workflow

### Scenario 1: Normal Traffic (No Alert)

**Via Frontend:**
1. Go to "Analyze Traffic" tab
2. Enter:
   - Source IP: `192.168.1.10`
   - Destination IP: `8.8.8.8`
   - Protocol: `TCP`
   - Payload: `Normal HTTP GET request`
3. Click "Analyze Traffic"
4. ✅ Result: "No anomalies detected" (green)

**Via API:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"192.168.1.10","dst_ip":"8.8.8.8","protocol":"TCP","payload":"Normal"}'
```

### Scenario 2: Suspicious IP Alert

**Via Frontend:**
1. Click "Example: Suspicious IP" button
2. Click "Analyze Traffic"
3. ✅ Result: HIGH severity alert displayed
4. Switch to "View Alerts" tab
5. ✅ Alert appears in table

**Via API:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"192.168.100.100","dst_ip":"10.0.0.1","protocol":"TCP","payload":"test"}'
```

### Scenario 3: Malicious DNS Query

**Via Frontend:**
1. Click "Example: Malicious DNS" button
2. Click "Analyze Traffic"
3. ✅ Result: HIGH severity DNS alert

**Via API:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"192.168.1.25","dst_ip":"8.8.8.8","protocol":"DNS","payload":"malware-site.tk"}'
```

### Scenario 4: Brute Force Attack Simulation

**Via Frontend:**
1. Click "Example: Login Attempt" button
2. Click "Analyze Traffic" **5 times**
3. ✅ Result: After 5th attempt, MEDIUM severity alert
4. Message: "Multiple login attempts detected"

**Via API:**
```bash
# Run this 5 times
for i in {1..5}; do
  curl -X POST http://localhost:8000/analyze \
    -H "Content-Type: application/json" \
    -d '{"src_ip":"203.0.114.50","dst_ip":"192.168.1.100","protocol":"HTTP","payload":"POST /login attempt='$i'"}'
done
```

---

## 🐛 Troubleshooting

### Problem: Frontend shows "Offline"

**Diagnosis:**
```bash
curl http://localhost:8000/health
```

**Solutions:**
1. Backend not running → Start backend: `python app.py`
2. Wrong port → Check `.env.local` has correct URL
3. CORS issue → Backend should allow all origins (already configured)

### Problem: "Failed to fetch data"

**Check 1: Backend API is accessible**
```bash
curl http://localhost:8000/health
```

**Check 2: Frontend environment variable**
```bash
cat frontend/.env.local
# Should show: NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Check 3: Browser console**
- Open browser DevTools (F12)
- Go to Console tab
- Look for error messages

### Problem: Port already in use

**Backend (port 8000):**
```bash
lsof -i :8000
kill -9 <PID>
```

**Frontend (port 3000):**
```bash
lsof -i :3000
kill -9 <PID>
```

Or use different ports:
```bash
# Backend
uvicorn app:app --port 8001

# Frontend
PORT=3001 npm run dev
```

### Problem: Changes not reflecting

**Backend:**
- Restart: `python app.py`
- Backend doesn't auto-reload by default

**Frontend:**
- Should hot-reload automatically
- If not, restart: `npm run dev`
- Clear cache: `rm -rf .next && npm run dev`

---

## 📊 Monitoring & Logs

### Backend Logs

Watch terminal where `python app.py` is running:
```
INFO:     127.0.0.1:54321 - "POST /analyze HTTP/1.1" 200 OK
INFO:     127.0.0.1:54322 - "GET /alerts HTTP/1.1" 200 OK
```

### Frontend Logs

Watch terminal where `npm run dev` is running:
```
○ Compiling / ...
✓ Compiled / in 234ms
```

### Browser Console

Open DevTools (F12) → Console tab to see:
- API requests
- Error messages
- State updates

---

## 🚀 Next Steps

### Stage 2: Dockerization

Create Docker containers for:
- Backend API
- Frontend dashboard
- Docker Compose for orchestration

### Stage 3: Cloud Integration

Add AWS integration:
- S3 for alert storage
- CloudWatch for monitoring
- Lambda for notifications
- Webhook support (Slack/Discord)

---

## 💡 Development Workflow

### Typical Day-to-Day Workflow

1. **Start both services** (Terminal 1 & 2)
2. **Make changes** to code
3. **Test in browser** (http://localhost:3000)
4. **Check backend logs** for API calls
5. **Check frontend console** for client errors
6. **Iterate and improve**

### Best Practices

- ✅ Keep backend running during development
- ✅ Use browser DevTools Network tab to debug API calls
- ✅ Test edge cases (invalid IPs, empty payloads)
- ✅ Clear alerts between test runs
- ✅ Monitor both terminal outputs

---

## 📚 Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **shadcn/ui Docs**: https://ui.shadcn.com/
- **Tailwind CSS**: https://tailwindcss.com/docs

---

## ✅ Full Stack Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Health indicator shows "Online"
- [ ] Statistics cards display correctly
- [ ] Can submit analysis via form
- [ ] Alerts appear in alerts table
- [ ] Auto-refresh works (wait 30s)
- [ ] Can clear alerts
- [ ] Example buttons work
- [ ] No console errors

---

**🎉 You're ready to detect network anomalies!**

Backend: http://localhost:8000/docs
Frontend: http://localhost:3000

