#!/bin/bash
# Start YouTube Downloader Web Application
# This script starts both the backend Flask server and the frontend React app

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          YouTube Downloader - Web Application Startup                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Running setup...${NC}"
    ./setup.sh
fi

# Activate virtual environment
echo -e "${GREEN}✓ Activating Python virtual environment...${NC}"
source venv/bin/activate

# Check if backend dependencies are installed
echo -e "${GREEN}✓ Checking backend dependencies...${NC}"
pip install -q flask flask-cors flask-socketio python-socketio 2>/dev/null || {
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    pip install flask flask-cors flask-socketio python-socketio
}

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Frontend dependencies not found. Installing...${NC}"
    cd frontend
    npm install
    cd ..
fi

# Create data directory for database
mkdir -p data
mkdir -p logs

# Start backend server in background
echo -e "${GREEN}✓ Starting Flask backend server on http://localhost:5001...${NC}"
cd src
python app.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend development server
echo -e "${GREEN}✓ Starting React frontend on http://localhost:3000...${NC}"
cd frontend

# Create .env file for React if it doesn't exist
if [ ! -f ".env" ]; then
    echo "REACT_APP_API_URL=http://localhost:5001" > .env
fi

npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ YouTube Downloader is now running!${NC}"
echo ""
echo -e "${BLUE}Frontend: ${NC}http://localhost:3000"
echo -e "${BLUE}Backend:  ${NC}http://localhost:5001"
echo ""
echo -e "${YELLOW}Note: Using port 5001 (macOS Control Center uses 5000)${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✓ All servers stopped. Goodbye!${NC}"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT TERM

# Wait for user to press Ctrl+C
wait
