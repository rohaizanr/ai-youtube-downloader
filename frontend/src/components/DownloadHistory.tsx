import React, { useState, useEffect } from 'react';
import { Download as DownloadIcon, Play, Trash2 } from 'lucide-react';
import { api } from '../services/api';
import { Download, Stats } from '../types';
import './DownloadHistory.css';

const DownloadHistory: React.FC = () => {
  const [downloads, setDownloads] = useState<Download[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDownloads();
    loadStats();
  }, []);

  const loadDownloads = async () => {
    try {
      const data = await api.getDownloads();
      setDownloads(data);
    } catch (error) {
      console.error('Failed to load downloads:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (loading) {
    return (
      <div className="download-history">
        <div className="loading">Loading download history...</div>
      </div>
    );
  }

  return (
    <div className="download-history">
      <div className="history-header">
        <h1>Download History</h1>
        {stats && (
          <div className="stats-summary">
            <div className="stat-item">
              <span className="stat-label">Total Downloads</span>
              <span className="stat-value">{stats.total_downloads}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Size</span>
              <span className="stat-value">{stats.total_size_formatted}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Conversations</span>
              <span className="stat-value">{stats.total_conversations}</span>
            </div>
          </div>
        )}
      </div>

      {downloads.length === 0 ? (
        <div className="no-downloads">
          <DownloadIcon size={48} />
          <h2>No downloads yet</h2>
          <p>Start a conversation and search for videos to download</p>
        </div>
      ) : (
        <div className="downloads-grid">
          {downloads.map((download) => (
            <div key={download.id} className="download-card">
              <div className="download-thumbnail">
                <img
                  src={download.video_thumbnail || 'https://via.placeholder.com/320x180?text=No+Thumbnail'}
                  alt={download.video_title}
                  onError={(e) => {
                    (e.target as HTMLImageElement).src =
                      'https://via.placeholder.com/320x180?text=No+Thumbnail';
                  }}
                />
                <div className="play-overlay">
                  <Play size={32} />
                </div>
              </div>
              <div className="download-info">
                <h3 className="download-title">{download.video_title}</h3>
                <p className="download-channel">{download.channel}</p>
                <div className="download-meta">
                  <span className="duration">{download.duration}</span>
                  <span className="separator">•</span>
                  <span className="file-size">{download.file_size_formatted}</span>
                  <span className="separator">•</span>
                  <span className="status">{download.status}</span>
                </div>
                <div className="download-date">
                  Downloaded: {formatDate(download.downloaded_at)}
                </div>
                <div className="download-actions">
                  <a
                    href={`http://localhost:5001/downloads/${download.file_path.split('/').pop()}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-action btn-play"
                  >
                    <Play size={16} />
                    Play
                  </a>
                  <button className="btn-action btn-delete">
                    <Trash2 size={16} />
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DownloadHistory;
