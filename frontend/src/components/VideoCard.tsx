import React from 'react';
import { Check, Play } from 'lucide-react';
import { Video } from '../types';
import './VideoCard.css';

// Helper function to extract video ID from URL
const extractVideoId = (url: string): string => {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]*)/,
    /youtube\.com\/embed\/([^&\n?]*)/,
    /youtube\.com\/v\/([^&\n?]*)/,
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match && match[1]) {
      return match[1];
    }
  }
  return '';
};

interface VideoCardProps {
  video: Video;
  selected: boolean;
  onToggle: () => void;
  onPreview: () => void;
  progress?: number;
}

const VideoCard: React.FC<VideoCardProps> = ({
  video,
  selected,
  onToggle,
  onPreview,
  progress,
}) => {
  const handlePreviewClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onPreview();
  };

  return (
    <div className={`video-card ${selected ? 'selected' : ''}`} onClick={onToggle}>
      <div className="video-thumbnail">
        <img 
          src={video.thumbnail || `https://img.youtube.com/vi/${extractVideoId(video.url)}/maxresdefault.jpg`} 
          alt={video.title}
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            if (!target.src.includes('hqdefault')) {
              target.src = `https://img.youtube.com/vi/${extractVideoId(video.url)}/hqdefault.jpg`;
            } else if (!target.src.includes('placeholder')) {
              target.src = 'https://via.placeholder.com/320x180/2563eb/ffffff?text=Video+Thumbnail';
            }
          }}
        />
        <button className="preview-button" onClick={handlePreviewClick} title="Preview video">
          <Play size={24} />
        </button>
        {selected && (
          <div className="selected-badge">
            <Check size={20} />
          </div>
        )}
        {progress !== undefined && progress > 0 && (
          <div className="download-progress">
            <div className="progress-bar" style={{ width: `${progress}%` }} />
            <span className="progress-text">{Math.round(progress)}%</span>
          </div>
        )}
        <span className="duration">{video.duration}</span>
      </div>
      <div className="video-info">
        <h4 className="video-title">{video.title}</h4>
        <p className="video-channel">{video.channel}</p>
        <div className="video-meta">
          <span>{video.views} views</span>
          <span>•</span>
          <span>{video.published}</span>
        </div>
      </div>
    </div>
  );
};

export default VideoCard;
