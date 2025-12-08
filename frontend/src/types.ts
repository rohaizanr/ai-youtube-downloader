export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface Video {
  title: string;
  url: string;
  duration: string;
  duration_seconds: number;
  views: string;
  channel: string;
  thumbnail: string;
  published: string;
}

export interface Download {
  id: string;
  video_url: string;
  video_title: string;
  video_thumbnail: string;
  file_path: string;
  file_size: number;
  file_size_formatted: string;
  duration: string;
  channel: string;
  status: string;
  downloaded_at: string;
}

export interface Config {
  downloads_dir: string;
  video_quality: string;
  audio_quality: string;
  output_format: string;
  max_duration: number;
  concurrent_downloads: number;
  log_level: string;
  ai_enabled: boolean;
  ai_provider: string;
  ai_search_enhancement: boolean;
  ai_result_filtering: boolean;
  ai_max_results_to_analyze: number;
}

export interface SearchResult {
  success: boolean;
  query: string;
  results: Video[];
  count: number;
}

export interface Stats {
  total_downloads: number;
  total_size: number;
  total_size_formatted: string;
  total_conversations: number;
}
