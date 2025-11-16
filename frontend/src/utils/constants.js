// API Base URL - Update this when backend is ready
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// API Endpoints
export const API_ENDPOINTS = {
  UPLOAD: '/api/upload',
  CHAT: '/api/chat',
  EXPORT: '/api/export',
  PREVIEW: '/api/preview',
};

// Supported video formats
export const SUPPORTED_VIDEO_FORMATS = [
  'video/mp4',
  'video/quicktime',
  'video/x-msvideo',
  'video/webm',
];

export const SUPPORTED_VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.webm'];

// Max file size (500MB)
export const MAX_FILE_SIZE = 500 * 1024 * 1024;

// Default subtitle styles
export const DEFAULT_SUBTITLE_STYLE = {
  fontFamily: 'Arial',
  fontSize: 24,
  color: '#FFFFFF',
  backgroundColor: 'rgba(0, 0, 0, 0.5)',
  position: 'bottom',
};

// Message types
export const MESSAGE_TYPES = {
  USER: 'user',
  AI: 'ai',
  SYSTEM: 'system',
};
