#!/bin/bash
# Test script for the new network-scan endpoint

echo "Testing NetSentry Network Scan Endpoint"
echo "========================================"
echo ""

# Check if the server is running
echo "1. Checking if server is running at http://localhost:8000..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ Server is running"
else
    echo "   ❌ Server is not running. Please start the server first:"
    echo "      python3 app.py"
    exit 1
fi

echo ""
echo "2. Testing /network-scan endpoint..."
echo "   This may take 10-30 seconds if nmap is installed..."
echo ""

# Call the network-scan endpoint
response=$(curl -s http://localhost:8000/network-scan)

# Check if the request was successful
if [ $? -eq 0 ]; then
    echo "   ✅ Network scan completed successfully"
    echo ""
    echo "3. Response Summary:"
    echo "   ==================="
    echo "$response" | python3 -m json.tool | head -50
    echo ""
    echo "   ... (truncated for brevity)"
    echo ""
    echo "4. Key Information:"
    echo "   =================="
    echo "   Local IP:      $(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('local_ip', 'N/A'))")"
    echo "   Network Range: $(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('network_range', 'N/A'))")"
    echo "   Gateway:       $(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('gateway', 'N/A'))")"
    echo "   Nmap Available: $(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('nmap_available', 'N/A'))")"
    echo "   Active Interfaces: $(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('network_metrics', {}).get('active_interfaces', 'N/A'))")"
    echo "   Devices Found: $(echo "$response" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('discovered_devices', [])))")"
    echo ""
    echo "✅ Test completed successfully!"
    echo ""
    echo "💡 Tip: Visit http://localhost:8000/docs to see the interactive API documentation"
else
    echo "   ❌ Network scan failed"
    exit 1
fi

