# NetSentry - Network Anomaly Detection System

Cloud-Based Network Traffic Analysis System with REST API

## Stage 1: Local REST API Service ✅

### Features
- **POST /analyze**: Analyze network traffic logs and detect anomalies
- **GET /alerts**: Retrieve all stored alerts
- **GET /health**: Health check endpoint
- **GET /stats**: System statistics
- **DELETE /alerts**: Clear all alerts (testing)

### Detection Rules Implemented
1. **Suspicious Source IPs**: Detects traffic from known malicious IPs
2. **Excessive Login Attempts**: Identifies brute-force attempts (5+ attempts)
3. **Suspicious DNS Queries**: Flags potentially malicious DNS lookups

---

## Setup Instructions

### 1. Install Dependencies

```bash
cd /Users/puneetgani/Documents/hackathon/netsentry
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python app.py
```

Or with uvicorn directly:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

### 3. Interactive API Documentation

Visit: `http://localhost:8000/docs` (Swagger UI)
Or: `http://localhost:8000/redoc` (ReDoc)

---

## Testing with cURL

### 1. Health Check

```bash
curl -X GET http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-03T12:34:56.789012",
  "version": "1.0.0"
}
```

---

### 2. Analyze Normal Traffic (No Alerts)

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.1.10",
    "dst_ip": "8.8.8.8",
    "protocol": "TCP",
    "payload": "Normal HTTP GET request"
  }'
```

**Expected Response:**
```json
{
  "status": "clean",
  "alerts": [],
  "message": "No anomalies detected"
}
```

---

### 3. Test Suspicious IP Detection

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

**Expected Response:**
```json
{
  "status": "alert",
  "alerts": [
    {
      "alert_id": "ALERT-20251003123456-1",
      "severity": "HIGH",
      "alert_type": "SUSPICIOUS_SOURCE_IP",
      "description": "Traffic detected from known suspicious IP: 192.168.100.100",
      "src_ip": "192.168.100.100",
      "dst_ip": "10.0.0.1",
      "protocol": "TCP",
      "timestamp": "2025-10-03T12:34:56.789012",
      "metadata": {
        "reason": "IP in blacklist"
      }
    }
  ],
  "message": "Detected 1 anomaly/anomalies"
}
```

---

### 4. Test Excessive Login Attempts

Send multiple login requests from the same IP:

```bash
# First attempt
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "203.0.114.50",
    "dst_ip": "192.168.1.100",
    "protocol": "HTTP",
    "payload": "POST /login username=admin&password=test1"
  }'

# Second attempt
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "203.0.114.50",
    "dst_ip": "192.168.1.100",
    "protocol": "HTTP",
    "payload": "POST /login username=admin&password=test2"
  }'

# Repeat 3 more times...
# On the 5th attempt, you'll get an alert:
```

**Expected Response (after 5th attempt):**
```json
{
  "status": "alert",
  "alerts": [
    {
      "alert_id": "ALERT-20251003123456-5",
      "severity": "MEDIUM",
      "alert_type": "EXCESSIVE_LOGIN_ATTEMPTS",
      "description": "Multiple login attempts detected from 203.0.114.50",
      "src_ip": "203.0.114.50",
      "dst_ip": "192.168.1.100",
      "protocol": "HTTP",
      "timestamp": "2025-10-03T12:34:56.789012",
      "metadata": {
        "attempt_count": 5,
        "payload_snippet": "POST /login username=admin&password=test2"
      }
    }
  ],
  "message": "Detected 1 anomaly/anomalies"
}
```

---

### 5. Test Suspicious DNS Query

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "src_ip": "192.168.1.25",
    "dst_ip": "8.8.8.8",
    "protocol": "DNS",
    "payload": "malware-c2server.tk"
  }'
```

**Expected Response:**
```json
{
  "status": "alert",
  "alerts": [
    {
      "alert_id": "ALERT-20251003123456-6",
      "severity": "HIGH",
      "alert_type": "SUSPICIOUS_DNS_QUERY",
      "description": "Suspicious DNS query detected: malware-c2server.tk",
      "src_ip": "192.168.1.25",
      "dst_ip": "8.8.8.8",
      "protocol": "DNS",
      "timestamp": "2025-10-03T12:34:56.789012",
      "metadata": {
        "query": "malware-c2server.tk",
        "matched_pattern": "\\.tk$"
      }
    }
  ],
  "message": "Detected 1 anomaly/anomalies"
}
```

---

### 6. Retrieve All Alerts

```bash
curl -X GET http://localhost:8000/alerts
```

**Expected Response:**
```json
{
  "total_alerts": 6,
  "filtered_count": 6,
  "alerts": [
    {
      "alert_id": "ALERT-20251003123456-1",
      "severity": "HIGH",
      "alert_type": "SUSPICIOUS_SOURCE_IP",
      ...
    },
    ...
  ]
}
```

---

### 7. Filter Alerts by Severity

```bash
curl -X GET "http://localhost:8000/alerts?severity=HIGH&limit=5"
```

---

### 8. Get System Statistics

```bash
curl -X GET http://localhost:8000/stats
```

**Expected Response:**
```json
{
  "total_alerts": 6,
  "by_severity": {
    "HIGH": 3,
    "MEDIUM": 3
  },
  "by_type": {
    "SUSPICIOUS_SOURCE_IP": 2,
    "EXCESSIVE_LOGIN_ATTEMPTS": 2,
    "SUSPICIOUS_DNS_QUERY": 2
  },
  "monitored_ips": 3,
  "suspicious_ip_count": 4
}
```

---

### 9. Clear All Alerts (Testing)

```bash
curl -X DELETE http://localhost:8000/alerts
```

**Expected Response:**
```json
{
  "message": "All alerts cleared",
  "status": "success"
}
```

---

## Testing Script (All-in-One)

Create a file `test_api.sh`:

```bash
#!/bin/bash

echo "=== NetSentry API Test Suite ==="
echo ""

BASE_URL="http://localhost:8000"

echo "1. Health Check"
curl -s -X GET $BASE_URL/health | jq .
echo -e "\n"

echo "2. Normal Traffic (should be clean)"
curl -s -X POST $BASE_URL/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"192.168.1.10","dst_ip":"8.8.8.8","protocol":"TCP","payload":"Normal traffic"}' | jq .
echo -e "\n"

echo "3. Suspicious IP Alert"
curl -s -X POST $BASE_URL/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"192.168.100.100","dst_ip":"10.0.0.1","protocol":"TCP","payload":"Suspicious"}' | jq .
echo -e "\n"

echo "4. Suspicious DNS Query"
curl -s -X POST $BASE_URL/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"192.168.1.25","dst_ip":"8.8.8.8","protocol":"DNS","payload":"malware-site.tk"}' | jq .
echo -e "\n"

echo "5. Multiple Login Attempts (5 times)"
for i in {1..5}; do
  curl -s -X POST $BASE_URL/analyze \
    -H "Content-Type: application/json" \
    -d "{\"src_ip\":\"203.0.114.50\",\"dst_ip\":\"192.168.1.100\",\"protocol\":\"HTTP\",\"payload\":\"POST /login attempt=$i\"}" > /dev/null
done
echo "Triggering 5th attempt..."
curl -s -X POST $BASE_URL/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"203.0.114.50","dst_ip":"192.168.1.100","protocol":"HTTP","payload":"POST /login attempt=5"}' | jq .
echo -e "\n"

echo "6. Get All Alerts"
curl -s -X GET $BASE_URL/alerts | jq .
echo -e "\n"

echo "7. Get Statistics"
curl -s -X GET $BASE_URL/stats | jq .
echo -e "\n"

echo "=== Test Complete ==="
```

Make it executable and run:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## Project Structure

```
netsentry/
├── app.py              # Main FastAPI application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── (Stage 2 files coming next)
```

---

## Next Steps

**Stage 2**: Dockerization
- Create Dockerfile
- Build and run container
- Test containerized service

**Stage 3**: Cloud Integration (AWS)
- S3 integration for alert storage
- Webhook notifications (Slack/Discord)
- CloudWatch monitoring
- Lambda triggers

---

## Architecture Notes

### Current Implementation (Stage 1)
- **In-memory storage**: Alerts stored in Python lists/dicts
- **Simple detection rules**: Pattern matching and threshold-based
- **REST API only**: All interactions via HTTP endpoints

### Planned Enhancements
- Persistent storage (Stage 3: S3)
- Machine learning-based detection
- Real-time streaming analysis
- Multi-tenant support
- Rate limiting and authentication

---

## Troubleshooting

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill it or use a different port
uvicorn app:app --port 8001
```

### Module not found
```bash
# Ensure you're in the correct directory and have installed requirements
pip install -r requirements.txt
```

### JSON parsing errors
- Ensure Content-Type header is set: `-H "Content-Type: application/json"`
- Check JSON syntax (use jq or online validators)

---

## API Response Codes

- `200 OK`: Successful request
- `422 Unprocessable Entity`: Invalid input (bad IP format, unknown protocol)
- `500 Internal Server Error`: Server-side error

---

**Ready for Stage 1 testing!** 🚀

Once you've tested the endpoints and confirmed everything works, let me know and we'll proceed to **Stage 2: Dockerization**.

