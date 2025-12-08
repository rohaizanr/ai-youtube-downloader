# 🔧 CORS Error Fixed!

## What was the problem?

You were seeing CORS (Cross-Origin Resource Sharing) errors because:

1. **Port Conflict**: macOS Control Center uses port 5000 by default
2. **CORS Configuration**: The backend needed proper CORS headers to allow requests from the frontend

## What was fixed?

✅ **Changed Backend Port**: Flask now runs on port **5001** instead of 5000  
✅ **Configured CORS**: Added proper CORS headers to allow frontend requests  
✅ **Updated Frontend**: All API calls now point to port 5001  
✅ **Fixed React Warnings**: Added ESLint disable comments for hook dependencies  

## How to use now?

### Start the application:
```bash
./start_web.sh
```

The script will automatically:
- Start backend on **http://localhost:5001**
- Start frontend on **http://localhost:3000**
- Configure CORS correctly

### Manual start (if needed):

**Backend:**
```bash
source venv/bin/activate
cd src
python app.py
# Backend will be at http://localhost:5001
```

**Frontend:**
```bash
cd frontend
npm start
# Frontend will be at http://localhost:3000
```

## Port Configuration

All files have been updated to use port **5001**:
- `src/app.py` - Backend server
- `frontend/.env` - Environment variables
- `frontend/src/services/api.ts` - API client
- `frontend/src/services/socket.ts` - WebSocket client
- `frontend/src/components/DownloadHistory.tsx` - Download links
- `start_web.sh` - Startup script

## Testing CORS

The backend now accepts requests from:
- `http://localhost:3000` (React dev server)
- `http://127.0.0.1:3000` (alternative localhost)

Supported methods:
- GET, POST, PUT, DELETE, OPTIONS

## Why port 5001?

macOS's **Control Center** (specifically AirPlay Receiver) uses port 5000 by default. This is a known issue on macOS Monterey and later. Using port 5001 avoids this conflict.

### To check what's using port 5000:
```bash
lsof -i :5000
```

You'll see something like:
```
COMMAND     PID     USER   FD   TYPE  DEVICE  SIZE/OFF NODE NAME
ControlCe 88862 rohaizan   10u  IPv4  ...     0t0  TCP *:commplex-main (LISTEN)
```

## Still having issues?

### Clear browser cache:
1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Check backend is running:
```bash
curl http://localhost:5001/api/health
```

Should return:
```json
{"status":"ok","message":"YouTube Downloader API is running"}
```

### Check frontend environment:
```bash
cat frontend/.env
```

Should show:
```
REACT_APP_API_URL=http://localhost:5001
```

### Restart everything:
```bash
# Kill any existing processes
lsof -ti:3000 | xargs kill -9
lsof -ti:5001 | xargs kill -9

# Start fresh
./start_web.sh
```

## Success! 🎉

Your CORS errors should now be resolved and you can use the web interface without issues!

Open http://localhost:3000 and start downloading videos! 🚀
