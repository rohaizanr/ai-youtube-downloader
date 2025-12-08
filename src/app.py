#!/usr/bin/env python3
"""
Flask Web Application for YouTube Downloader
Provides a ChatGPT-like interface for searching and downloading YouTube videos
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import uuid

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from youtube_downloader import YouTubeDownloader
from utils import format_file_size, get_video_thumbnail

app = Flask(__name__)

# Configure CORS to allow requests from React frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    },
    r"/downloads/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Configure SocketIO with CORS
socketio = SocketIO(app, 
                   cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
                   async_mode='threading',
                   logger=True,
                   engineio_logger=True)

# Database setup
DB_PATH = Path('data/app.db')
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    """Initialize SQLite database for chat history and downloads"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Chat conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Chat messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    ''')
    
    # Downloads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            video_url TEXT,
            video_title TEXT,
            video_thumbnail TEXT,
            file_path TEXT,
            file_size INTEGER,
            duration TEXT,
            channel TEXT,
            status TEXT,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Global downloader instance
downloader = None

def get_downloader():
    """Get or create downloader instance"""
    global downloader
    if downloader is None:
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
        downloader = YouTubeDownloader(str(config_path))
    return downloader

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'YouTube Downloader API is running'})

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, created_at, updated_at 
        FROM conversations 
        ORDER BY updated_at DESC
    ''')
    
    conversations = []
    for row in cursor.fetchall():
        conversations.append({
            'id': row[0],
            'title': row[1],
            'created_at': row[2],
            'updated_at': row[3]
        })
    
    conn.close()
    return jsonify(conversations)

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation"""
    data = request.json
    conversation_id = str(uuid.uuid4())
    title = data.get('title', 'New Chat')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversations (id, title) 
        VALUES (?, ?)
    ''', (conversation_id, title))
    
    conn.commit()
    conn.close()
    
    return jsonify({'id': conversation_id, 'title': title})

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation with messages"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get conversation details
    cursor.execute('SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?', (conversation_id,))
    conv_row = cursor.fetchone()
    
    if not conv_row:
        conn.close()
        return jsonify({'error': 'Conversation not found'}), 404
    
    # Get messages
    cursor.execute('''
        SELECT id, role, content, created_at 
        FROM messages 
        WHERE conversation_id = ? 
        ORDER BY created_at ASC
    ''', (conversation_id,))
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            'id': row[0],
            'role': row[1],
            'content': row[2],
            'created_at': row[3]
        })
    
    conn.close()
    
    return jsonify({
        'id': conv_row[0],
        'title': conv_row[1],
        'created_at': conv_row[2],
        'updated_at': conv_row[3],
        'messages': messages
    })

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation and its messages"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
    cursor.execute('DELETE FROM downloads WHERE conversation_id = ?', (conversation_id,))
    cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/conversations/<conversation_id>/messages', methods=['POST'])
def add_message(conversation_id):
    """Add a message to a conversation"""
    data = request.json
    message_id = str(uuid.uuid4())
    role = data.get('role', 'user')
    content = data.get('content', '')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO messages (id, conversation_id, role, content) 
        VALUES (?, ?, ?, ?)
    ''', (message_id, conversation_id, role, content))
    
    # Update conversation timestamp
    cursor.execute('''
        UPDATE conversations 
        SET updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (conversation_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'id': message_id, 'role': role, 'content': content})

@app.route('/api/search', methods=['POST'])
def search_videos():
    """Search for YouTube videos"""
    data = request.json
    query = data.get('query', '')
    max_results = data.get('max_results', 10)
    conversation_id = data.get('conversation_id')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        dl = get_downloader()
        videos = dl.search_videos(query, max_results, skip_downloaded=True)
        
        # Save assistant response
        if conversation_id:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            message_id = str(uuid.uuid4())
            content = json.dumps({
                'type': 'search_results',
                'query': query,
                'results': videos
            })
            
            cursor.execute('''
                INSERT INTO messages (id, conversation_id, role, content) 
                VALUES (?, ?, ?, ?)
            ''', (message_id, conversation_id, 'assistant', content))
            
            conn.commit()
            conn.close()
        
        return jsonify({
            'success': True,
            'query': query,
            'results': videos,
            'count': len(videos)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download_videos():
    """Download videos"""
    data = request.json
    video_urls = data.get('video_urls', [])
    conversation_id = data.get('conversation_id')
    
    if not video_urls:
        return jsonify({'error': 'Video URLs are required'}), 400
    
    try:
        dl = get_downloader()
        
        # Start download in background and emit progress via WebSocket
        def download_with_progress():
            results = {'successful': [], 'failed': []}
            
            for idx, url in enumerate(video_urls):
                def progress_callback(d):
                    if d['status'] == 'downloading':
                        progress = 0
                        if 'total_bytes' in d and d['total_bytes']:
                            progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        elif '_percent_str' in d:
                            try:
                                progress = float(d['_percent_str'].strip('%'))
                            except:
                                pass
                        
                        socketio.emit('download_progress', {
                            'url': url,
                            'index': idx,
                            'total': len(video_urls),
                            'progress': progress
                        })
                
                success, result = dl.download_video(url, progress_callback)
                
                if success:
                    # Get video info
                    video_info = None
                    for video in dl.downloaded_videos:
                        if video['url'] == url:
                            video_info = video
                            break
                    
                    if video_info:
                        # Save to database
                        download_id = str(uuid.uuid4())
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        
                        file_size = 0
                        if os.path.exists(result):
                            file_size = os.path.getsize(result)
                        
                        cursor.execute('''
                            INSERT INTO downloads 
                            (id, conversation_id, video_url, video_title, file_path, file_size, status) 
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (download_id, conversation_id, url, video_info.get('title'), result, file_size, 'completed'))
                        
                        conn.commit()
                        conn.close()
                    
                    results['successful'].append({'url': url, 'file': result})
                else:
                    results['failed'].append({'url': url, 'error': result})
                
                socketio.emit('download_complete', {
                    'url': url,
                    'success': success,
                    'result': result
                })
            
            socketio.emit('all_downloads_complete', results)
        
        thread = threading.Thread(target=download_with_progress)
        thread.start()
        
        return jsonify({'success': True, 'message': 'Download started'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/downloads', methods=['GET'])
def get_downloads():
    """Get download history"""
    conversation_id = request.args.get('conversation_id')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if conversation_id:
        cursor.execute('''
            SELECT id, video_url, video_title, video_thumbnail, file_path, 
                   file_size, duration, channel, status, downloaded_at 
            FROM downloads 
            WHERE conversation_id = ? 
            ORDER BY downloaded_at DESC
        ''', (conversation_id,))
    else:
        cursor.execute('''
            SELECT id, video_url, video_title, video_thumbnail, file_path, 
                   file_size, duration, channel, status, downloaded_at 
            FROM downloads 
            ORDER BY downloaded_at DESC
        ''')
    
    downloads = []
    for row in cursor.fetchall():
        downloads.append({
            'id': row[0],
            'video_url': row[1],
            'video_title': row[2],
            'video_thumbnail': row[3],
            'file_path': row[4],
            'file_size': row[5],
            'file_size_formatted': format_file_size(row[5]) if row[5] else '0 B',
            'duration': row[6],
            'channel': row[7],
            'status': row[8],
            'downloaded_at': row[9]
        })
    
    conn.close()
    return jsonify(downloads)

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    dl = get_downloader()
    return jsonify(dl.config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    data = request.json
    
    try:
        import yaml
        config_path = Path('config/config.yaml')
        
        # Load current config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update with new values
        config.update(data)
        
        # Save back to file
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        # Reload downloader with new config
        global downloader
        downloader = YouTubeDownloader()
        
        return jsonify({'success': True, 'config': config})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/downloads/<path:filename>', methods=['GET'])
def serve_download(filename):
    """Serve downloaded video files"""
    downloads_dir = Path('downloads')
    return send_from_directory(downloads_dir, filename)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get total downloads
    cursor.execute('SELECT COUNT(*) FROM downloads')
    total_downloads = cursor.fetchone()[0]
    
    # Get total file size
    cursor.execute('SELECT SUM(file_size) FROM downloads')
    total_size = cursor.fetchone()[0] or 0
    
    # Get total conversations
    cursor.execute('SELECT COUNT(*) FROM conversations')
    total_conversations = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_downloads': total_downloads,
        'total_size': total_size,
        'total_size_formatted': format_file_size(total_size),
        'total_conversations': total_conversations
    })

# WebSocket events

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'message': 'Connected to YouTube Downloader'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    # Use port 5001 instead of 5000 (macOS Control Center uses 5000)
    PORT = 5001
    print("=" * 70)
    print("🚀 YouTube Downloader Backend Server")
    print("=" * 70)
    print(f"Backend API: http://localhost:{PORT}")
    print(f"Frontend: http://localhost:3000")
    print("=" * 70)
    socketio.run(app, debug=True, host='0.0.0.0', port=PORT, allow_unsafe_werkzeug=True)
