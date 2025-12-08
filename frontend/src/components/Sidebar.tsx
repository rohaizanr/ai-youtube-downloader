import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { MessageSquare, Download, Settings as SettingsIcon, Plus, Trash2, PanelLeft } from 'lucide-react';
import { Conversation } from '../types';
import './Sidebar.css';

interface SidebarProps {
  conversations: Conversation[];
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  isOpen,
  onToggle,
}) => {
  const location = useLocation();

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <>
      <button className="sidebar-toggle" onClick={onToggle}>
        <PanelLeft size={24} />
      </button>

      {isOpen && <div className="sidebar-overlay" onClick={onToggle} />}

      <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="app-title-container">
            <h2>YouTube Downloader</h2>
            <span className="ai-powered-badge">AI-Powered</span>
          </div>
          <button className="btn-new-chat" onClick={onNewConversation}>
            <Plus size={20} />
            <span>New Chat</span>
          </button>
        </div>

        <nav className="sidebar-nav">
          <Link 
            to="/" 
            className={`nav-item ${location.pathname === '/' ? 'active' : ''}`}
          >
            <MessageSquare size={20} />
            <span>Chat</span>
          </Link>
          <Link 
            to="/history" 
            className={`nav-item ${location.pathname === '/history' ? 'active' : ''}`}
          >
            <Download size={20} />
            <span>Download History</span>
          </Link>
          <Link 
            to="/settings" 
            className={`nav-item ${location.pathname === '/settings' ? 'active' : ''}`}
          >
            <SettingsIcon size={20} />
            <span>Settings</span>
          </Link>
        </nav>

        <div className="conversations-list">
          <h3>Recent Conversations</h3>
          {conversations.length === 0 ? (
            <p className="no-conversations">No conversations yet</p>
          ) : (
            <div className="conversations">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`conversation-item ${
                    conv.id === currentConversationId ? 'active' : ''
                  }`}
                  onClick={() => onSelectConversation(conv.id)}
                >
                  <div className="conversation-content">
                    <span className="conversation-title">{conv.title}</span>
                    <span className="conversation-date">
                      {formatDate(conv.updated_at)}
                    </span>
                  </div>
                  <button
                    className="btn-delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (window.confirm('Delete this conversation?')) {
                        onDeleteConversation(conv.id);
                      }
                    }}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;
