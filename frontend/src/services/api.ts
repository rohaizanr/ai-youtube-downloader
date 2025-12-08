import axios from 'axios';
import { Conversation, Message, Config, SearchResult, Download, Stats } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout for AI processing
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health check
  healthCheck: async () => {
    const response = await axiosInstance.get('/api/health');
    return response.data;
  },

  // Conversations
  getConversations: async (): Promise<Conversation[]> => {
    const response = await axiosInstance.get('/api/conversations');
    return response.data;
  },

  createConversation: async (title: string): Promise<Conversation> => {
    const response = await axiosInstance.post('/api/conversations', { title });
    return response.data;
  },

  getConversation: async (id: string): Promise<Conversation & { messages: Message[] }> => {
    const response = await axiosInstance.get(`/api/conversations/${id}`);
    return response.data;
  },

  deleteConversation: async (id: string): Promise<void> => {
    await axiosInstance.delete(`/api/conversations/${id}`);
  },

  // Messages
  addMessage: async (conversationId: string, role: string, content: string): Promise<Message> => {
    const response = await axiosInstance.post(`/api/conversations/${conversationId}/messages`, {
      role,
      content,
    });
    return response.data;
  },

  // Search
  searchVideos: async (query: string, conversationId: string, maxResults: number = 10): Promise<SearchResult> => {
    const response = await axiosInstance.post('/api/search', {
      query,
      conversation_id: conversationId,
      max_results: maxResults,
    });
    return response.data;
  },

  // Download
  downloadVideos: async (videoUrls: string[], conversationId: string): Promise<{ success: boolean; message: string }> => {
    const response = await axiosInstance.post('/api/download', {
      video_urls: videoUrls,
      conversation_id: conversationId,
    });
    return response.data;
  },

  // Downloads history
  getDownloads: async (conversationId?: string): Promise<Download[]> => {
    const url = conversationId 
      ? `/api/downloads?conversation_id=${conversationId}` 
      : '/api/downloads';
    const response = await axiosInstance.get(url);
    return response.data;
  },

  // Config
  getConfig: async (): Promise<Config> => {
    const response = await axiosInstance.get('/api/config');
    return response.data;
  },

  updateConfig: async (config: Partial<Config>): Promise<{ success: boolean; config: Config }> => {
    const response = await axiosInstance.post('/api/config', config);
    return response.data;
  },

  // Stats
  getStats: async (): Promise<Stats> => {
    const response = await axiosInstance.get('/api/stats');
    return response.data;
  },
};
