import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader, X } from 'lucide-react';
import { api } from '../services/api';
import { socketService } from '../services/socket';
import { Message, Video } from '../types';
import VideoCard from './VideoCard';
import './ChatInterface.css';

interface ChatInterfaceProps {
  conversationId: string;
  onNewConversation: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  conversationId,
  onNewConversation,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<Video[]>([]);
  const [selectedVideos, setSelectedVideos] = useState<Set<string>>(new Set());
  const [downloading, setDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState<{ [key: string]: number }>({});
  const [previewVideo, setPreviewVideo] = useState<Video | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversation();
    
    // Connect to WebSocket
    socketService.connect();
    
    // Listen for download progress
    socketService.on('download_progress', (data: any) => {
      setDownloadProgress((prev) => ({
        ...prev,
        [data.url]: data.progress,
      }));
    });

    socketService.on('download_complete', (data: any) => {
      if (data.success) {
        addSystemMessage(`Downloaded: ${data.result}`);
      } else {
        addSystemMessage(`Failed to download: ${data.error}`, true);
      }
    });

    socketService.on('all_downloads_complete', () => {
      setDownloading(false);
      setDownloadProgress({});
      setSelectedVideos(new Set());
      addSystemMessage('All downloads completed!');
    });

    return () => {
      socketService.off('download_progress');
      socketService.off('download_complete');
      socketService.off('all_downloads_complete');
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversation = async () => {
    try {
      const data = await api.getConversation(conversationId);
      const parsedMessages = data.messages.map((msg) => {
        try {
          const content = JSON.parse(msg.content);
          if (content.type === 'search_results') {
            setSearchResults(content.results);
          }
          return msg;
        } catch {
          return msg;
        }
      });
      setMessages(parsedMessages);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const addSystemMessage = (content: string, isError: boolean = false) => {
    const systemMsg: Message = {
      id: Date.now().toString(),
      role: 'system',
      content: isError ? `Error: ${content}` : content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, systemMsg]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);
    setSearchResults([]);
    setSelectedVideos(new Set());

    // Add user message
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    // Save user message
    await api.addMessage(conversationId, 'user', userMessage);

    try {
      // Search for videos
      const result = await api.searchVideos(userMessage, conversationId, 10);
      
      if (result.success && result.results.length > 0) {
        setSearchResults(result.results);
        
        const assistantMsg: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: `Found ${result.count} videos matching "${result.query}". Select the videos you want to download:`,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } else {
        const assistantMsg: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: `No videos found for "${userMessage}". Try a different search query.`,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      }
    } catch (error: any) {
      const errorMsg: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Error: ${error.message || 'Failed to search videos'}`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const toggleVideoSelection = (videoUrl: string) => {
    const newSelected = new Set(selectedVideos);
    if (newSelected.has(videoUrl)) {
      newSelected.delete(videoUrl);
    } else {
      newSelected.add(videoUrl);
    }
    setSelectedVideos(newSelected);
  };

  const handlePreview = (video: Video) => {
    setPreviewVideo(video);
  };

  const closePreview = () => {
    setPreviewVideo(null);
  };

  const handleDownload = async () => {
    if (selectedVideos.size === 0) {
      addSystemMessage('Please select at least one video to download', true);
      return;
    }

    setDownloading(true);
    const videoUrls = Array.from(selectedVideos);

    try {
      await api.downloadVideos(videoUrls, conversationId);
      addSystemMessage(`Starting download of ${videoUrls.length} video(s)...`);
    } catch (error: any) {
      setDownloading(false);
      addSystemMessage(`Download failed: ${error.message}`, true);
    }
  };

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>Welcome! 👋</h2>
            <p>Search for YouTube videos by typing your query below.</p>
            <div className="example-queries">
              <h3>Try these:</h3>
              <button onClick={() => setInput('funny cat videos in 9:16 only')}>
                funny cat videos in 9:16 only
              </button>
              <button onClick={() => setInput('python tutorials in bahasa malaysia')}>
                python tutorials in bahasa malaysia
              </button>
              <button onClick={() => setInput('semua resipi nasi chef wan sahaja')}>
                semua resipi nasi chef wan sahaja
              </button>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.content}
            </div>
            <div className="message-time">
              {new Date(msg.created_at).toLocaleTimeString()}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <Loader className="spinner" size={20} />
              <span>Searching for videos...</span>
            </div>
          </div>
        )}

        {searchResults.length > 0 && (
          <div className="search-results">
            <div className="results-header">
              <h3>Select videos to download:</h3>
              {selectedVideos.size > 0 && (
                <button
                  className="btn-download"
                  onClick={handleDownload}
                  disabled={downloading}
                >
                  {downloading ? (
                    <>
                      <Loader className="spinner" size={16} />
                      Downloading...
                    </>
                  ) : (
                    `Download Selected (${selectedVideos.size})`
                  )}
                </button>
              )}
            </div>
            <div className="video-grid">
              {searchResults.map((video) => (
                <VideoCard
                  key={video.url}
                  video={video}
                  selected={selectedVideos.has(video.url)}
                  onToggle={() => toggleVideoSelection(video.url)}
                  onPreview={() => handlePreview(video)}
                  progress={downloadProgress[video.url]}
                />
              ))}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {previewVideo && (
        <div className="video-preview-modal" onClick={closePreview}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closePreview}>
              <X size={24} />
            </button>
            <div className="modal-video-container">
              <iframe
                src={`https://www.youtube.com/embed/${previewVideo.url.split('v=')[1]?.split('&')[0]}?autoplay=1`}
                title={previewVideo.title}
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
            <div className="modal-video-info">
              <h3>{previewVideo.title}</h3>
              <p className="modal-channel">{previewVideo.channel}</p>
              <div className="modal-meta">
                <span>{previewVideo.views} views</span>
                <span>•</span>
                <span>{previewVideo.duration}</span>
                <span>•</span>
                <span>{previewVideo.published}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <form className="input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Search for YouTube videos..."
          disabled={loading}
          className="chat-input"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="btn-send"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
