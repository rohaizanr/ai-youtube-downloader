# YouTube Downloader - Web Interface

A modern, ChatGPT-like web interface for searching and downloading YouTube videos with AI-powered search enhancement.

## 🎨 Features

### 💬 Chat Interface
- **ChatGPT-style UI** - Natural conversation interface for searching videos
- **Real-time search** - Instant video results with thumbnails
- **Smart selection** - Select multiple videos for batch download
- **Live progress** - Real-time download progress tracking via WebSocket

### 📚 Sidebar Navigation
- **New Chat Button** - Start fresh conversations instantly
- **Conversation History** - Access all past searches and downloads
- **Download History** - Browse all downloaded videos with thumbnails
- **Settings Page** - Configure app behavior and preferences

### 📥 Download History
- **Visual Gallery** - Grid view of all downloaded videos with screenshots
- **Metadata Display** - See video title, channel, duration, file size
- **Quick Actions** - Play videos directly or delete from history
- **Statistics** - Track total downloads, storage used, and more

### ⚙️ Settings Page
- **Download Configuration** - Set quality, format, max duration
- **AI Settings** - Enable/disable AI-powered search enhancement
- **Directory Management** - Choose download location
- **Performance Tuning** - Adjust concurrent downloads

## 🚀 Quick Start

### Prerequisites
- macOS
- Python 3.8+
- Node.js 14+
- ffmpeg (`brew install ffmpeg`)

### Installation & Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd youtube-downloader-automation
```

2. **Run the setup script** (one-time setup)
```bash
./setup.sh
```

3. **Start the web application**
```bash
./start_web.sh
```

The script will automatically:
- Activate the Python virtual environment
- Install backend dependencies (Flask, SocketIO)
- Install frontend dependencies (React, TypeScript)
- Start the Flask backend server (port 5000)
- Start the React frontend (port 3000)
- Open your browser to http://localhost:3000

## 🎯 Usage

### Starting a Conversation
1. Click **"New Chat"** button in the sidebar
2. Type your search query (e.g., "funny cat videos", "python tutorials")
3. Press Enter or click Send

### Downloading Videos
1. Review the search results displayed as cards
2. Click on videos to select them (checkmark appears)
3. Click **"Download Selected (X)"** button
4. Watch real-time progress in the video cards
5. View completed downloads in the History page

### Managing Settings
1. Click **Settings** in the sidebar
2. Adjust your preferences:
   - Video quality (Best, 720p, 480p, 360p)
   - Output format (MP4, WebM, MKV)
   - Maximum video duration
   - AI enhancement options
3. Click **"Save Changes"** to apply

### Browsing History
1. Click **Download History** in the sidebar
2. View all downloaded videos in a grid
3. Click **Play** to watch a video
4. Click **Delete** to remove from history

## 📁 Project Structure

```
youtube-downloader-automation/
├── src/
│   ├── app.py                  # Flask backend server
│   ├── main.py                 # CLI interface (legacy)
│   ├── youtube_downloader.py   # Core download logic
│   ├── ai_helper.py            # AI search enhancement
│   └── utils.py                # Utility functions
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.tsx            # Sidebar navigation
│   │   │   ├── ChatInterface.tsx      # Main chat UI
│   │   │   ├── VideoCard.tsx          # Video display card
│   │   │   ├── DownloadHistory.tsx    # History page
│   │   │   └── Settings.tsx           # Settings page
│   │   ├── services/
│   │   │   ├── api.ts                 # API client
│   │   │   └── socket.ts              # WebSocket client
│   │   ├── types.ts                   # TypeScript types
│   │   └── App.tsx                    # Main app component
│   └── package.json
├── config/
│   └── config.yaml             # Application configuration
├── data/
│   └── app.db                  # SQLite database
├── downloads/                  # Downloaded videos
├── logs/                       # Application logs
├── start_web.sh               # Web app startup script
└── README_WEB.md              # This file
```

## 🛠 Technology Stack

### Backend
- **Flask** - Python web framework
- **Flask-SocketIO** - Real-time WebSocket communication
- **SQLite** - Database for conversations and history
- **yt-dlp** - YouTube video downloader
- **Google Gemini AI** - Search enhancement (optional)

### Frontend
- **React** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Socket.IO Client** - Real-time updates
- **Axios** - HTTP client
- **React Router** - Navigation
- **Lucide React** - Modern icons

## 🔌 API Endpoints

### Conversations
- `GET /api/conversations` - List all conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations/:id` - Get conversation details
- `DELETE /api/conversations/:id` - Delete conversation

### Messages
- `POST /api/conversations/:id/messages` - Add message

### Search & Download
- `POST /api/search` - Search for videos
- `POST /api/download` - Download selected videos

### Downloads History
- `GET /api/downloads` - Get all downloads
- `GET /api/downloads?conversation_id=:id` - Get conversation downloads

### Configuration
- `GET /api/config` - Get current config
- `POST /api/config` - Update configuration

### Statistics
- `GET /api/stats` - Get app statistics

### WebSocket Events
- `download_progress` - Real-time download progress
- `download_complete` - Single download completed
- `all_downloads_complete` - All downloads finished

## ⚡ Performance Tips

1. **Adjust concurrent downloads** in Settings (default: 3)
2. **Lower video quality** for faster downloads
3. **Enable AI filtering** for better search results
4. **Clear old downloads** to save disk space

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if Python dependencies are installed
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start
```bash
cd frontend
npm install
npm start
```

### Port already in use
```bash
# Kill process on port 5000 (backend)
lsof -ti:5000 | xargs kill -9

# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

### Database errors
```bash
# Reset database
rm data/app.db
# Restart the app - database will be recreated
```

### WebSocket connection issues
- Check that backend is running on port 5000
- Verify `REACT_APP_API_URL` in `frontend/.env`
- Check browser console for errors

## 🔒 Security Notes

1. **API Keys** - Never commit API keys to git
   - Use `.env` file for environment variables
   - Add `.env` to `.gitignore`

2. **Downloads** - The app saves videos to `downloads/` directory
   - Ensure you have permission to download content
   - Respect copyright and Terms of Service

3. **Database** - SQLite database stored in `data/app.db`
   - Contains conversation history only
   - No sensitive user data stored

## 📝 Development

### Running in Development Mode

**Backend:**
```bash
source venv/bin/activate
cd src
python app.py
```

**Frontend:**
```bash
cd frontend
npm start
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
```

The build artifacts will be in `frontend/build/` directory.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see `LICENSE` file for details.

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by ChatGPT's interface design
- Powered by yt-dlp for reliable downloads
- AI enhancement by Google Gemini

---

**Enjoy downloading! 🎬**

For CLI usage, see the main `README.md` file.
