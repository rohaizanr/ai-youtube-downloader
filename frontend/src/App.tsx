import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Sparkles, Plus } from 'lucide-react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import DownloadHistory from './components/DownloadHistory';
import Settings from './components/Settings';
import { Conversation } from './types';
import { api } from './services/api';
import './App.css';

function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth > 768);

  useEffect(() => {
    loadConversations();
    
    const handleResize = () => {
      if (window.innerWidth <= 768) {
        setSidebarOpen(false);
      } else {
        setSidebarOpen(true);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSelectConversation = (id: string) => {
    setCurrentConversationId(id);
    if (window.innerWidth <= 768) {
      setSidebarOpen(false);
    }
  };

  const loadConversations = async () => {
    try {
      const data = await api.getConversations();
      setConversations(data);
      
      // If no current conversation and conversations exist, select the first one
      if (!currentConversationId && data.length > 0) {
        setCurrentConversationId(data[0].id);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const createNewConversation = async () => {
    try {
      const newConv = await api.createConversation('New Chat');
      setConversations([newConv, ...conversations]);
      setCurrentConversationId(newConv.id);
      if (window.innerWidth <= 768) {
        setSidebarOpen(false);
      }
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const deleteConversation = async (id: string) => {
    try {
      await api.deleteConversation(id);
      setConversations(conversations.filter(c => c.id !== id));
      
      // If deleted conversation was active, select another
      if (currentConversationId === id) {
        const remaining = conversations.filter(c => c.id !== id);
        setCurrentConversationId(remaining.length > 0 ? remaining[0].id : null);
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  return (
    <Router>
      <div className="app">
        <Sidebar
          conversations={conversations}
          currentConversationId={currentConversationId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={createNewConversation}
          onDeleteConversation={deleteConversation}
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
        />
        
        <div className={`main-content ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
          <Routes>
            <Route 
              path="/" 
              element={
                currentConversationId ? (
                  <ChatInterface 
                    conversationId={currentConversationId}
                    onNewConversation={createNewConversation}
                  />
                ) : (
                  <div className="welcome-screen">
                    <div className="welcome-decoration"></div>
                    <div className="welcome-header">
                      <div className="icon-container">
                        <Sparkles size={48} className="welcome-icon" />
                      </div>
                      <h1>YouTube Downloader</h1>
                      <span className="ai-powered-badge-large">AI-POWERED</span>
                    </div>
                    <p>Start a new conversation to search and download videos</p>
                    <button className="btn-primary" onClick={createNewConversation}>
                      <Plus size={20} />
                      New Chat
                    </button>
                  </div>
                )
              } 
            />
            <Route path="/history" element={<DownloadHistory />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
