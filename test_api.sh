#!/bin/bash

echo "=== NetSentry API Test Suite ==="
echo ""

BASE_URL="http://localhost:8000"

echo "1. Health Check"
curl -s -X GET $BASE_URL/health | python3 -m json.tool
echo -e "\n"

echo "2. Normal Traffic (should be clean)"
curl -s -X POST $BASE_URL/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"192.168.1.10","dst_ip":"8.8.8.8","protocol":"TCP","payload":"Normal traffic"}' | python3 -m json.tool
echo -e "\n"

echo "3. Suspicious IP Alert"
curl -s -X POST $BASE_URL/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"192.168.100.100","dst_ip":"10.0.0.1","protocol":"TCP","payload":"Suspicious"}' | python3 -m json.tool
echo -e "\n"

echo "4. Suspicious DNS Query"
curl -s -X POST $BASE_URL/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"192.168.1.25","dst_ip":"8.8.8.8","protocol":"DNS","payload":"malware-site.tk"}' | python3 -m json.tool
echo -e "\n"

echo "5. Multiple Login Attempts (5 times)"
for i in {1..4}; do
  curl -s -X POST $BASE_URL/analyze \
    -H "Content-Type: application/json" \
    -d "{\"src_ip\":\"203.0.114.50\",\"dst_ip\":\"192.168.1.100\",\"protocol\":\"HTTP\",\"payload\":\"POST /login attempt=$i\"}" > /dev/null
done
echo "Triggering 5th attempt..."
curl -s -X POST $BASE_URL/analyze \
  -H "Content-Type: application/json" \
  -d '{"src_ip":"203.0.114.50","dst_ip":"192.168.1.100","protocol":"HTTP","payload":"POST /login attempt=5"}' | python3 -m json.tool
echo -e "\n"

echo "6. Get All Alerts"
curl -s -X GET $BASE_URL/alerts | python3 -m json.tool
echo -e "\n"

echo "7. Get Statistics"
curl -s -X GET $BASE_URL/stats | python3 -m json.tool
echo -e "\n"

echo "=== Test Complete ==="

