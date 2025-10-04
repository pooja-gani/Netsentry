#!/bin/bash

echo "═══════════════════════════════════════════════════════"
echo "  NetSentry - Starting Full Stack Application"
echo "═══════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found:${NC} $(python3 --version)"
echo -e "${GREEN}✓ Node.js found:${NC} $(node --version)"
echo ""

# Check if backend dependencies are installed
echo "Checking backend dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Backend dependencies not installed${NC}"
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
else
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
fi

# Check if frontend dependencies are installed
echo "Checking frontend dependencies..."
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠ Frontend dependencies not installed${NC}"
    echo "Installing frontend dependencies..."
    cd frontend && npm install && cd ..
else
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Starting Services..."
echo "═══════════════════════════════════════════════════════"
echo ""

# Start backend in background
echo -e "${YELLOW}→ Starting Backend API on port 8000...${NC}"
python3 app.py > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Backend is running: http://localhost:8000${NC}"
else
    echo -e "${RED}✗ Backend failed to start${NC}"
    echo "Check backend.log for details"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo -e "${YELLOW}→ Starting Frontend on port 3000...${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  🚀 NetSentry is Running!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Backend API:${NC}     http://localhost:8000"
echo -e "${GREEN}API Docs:${NC}        http://localhost:8000/docs"
echo -e "${GREEN}Frontend:${NC}        http://localhost:3000"
echo ""
echo "Logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Save PIDs to file for cleanup
echo "$BACKEND_PID" > .pids
echo "$FRONTEND_PID" >> .pids

# Wait for Ctrl+C
trap cleanup INT

cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    # Also kill any child processes
    pkill -P $BACKEND_PID 2>/dev/null
    pkill -P $FRONTEND_PID 2>/dev/null
    rm -f .pids
    echo "Services stopped."
    exit 0
}

# Keep script running
while true; do
    sleep 1
done

