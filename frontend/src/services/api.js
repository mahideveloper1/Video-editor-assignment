import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../utils/constants';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens if needed
apiClient.interceptors.request.use(
  (config) => {
    // You can add authorization headers here if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error:', error.request);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Upload video file
 * @param {File} file - Video file to upload
 * @param {Function} onProgress - Progress callback
 * @returns {Promise} Upload response
 */
export const uploadVideo = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await apiClient.post(API_ENDPOINTS.UPLOAD, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        if (onProgress) {
          onProgress(percentCompleted);
        }
      },
    });

    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.message || 'Failed to upload video'
    );
  }
};

/**
 * Send chat message/prompt
 * @param {string} sessionId - Video session ID
 * @param {string} message - User message/prompt
 * @param {string} videoId - Video ID (optional, for backward compatibility)
 * @returns {Promise} Chat response
 */
export const sendChatMessage = async (sessionId, message, videoId) => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.CHAT, {
      session_id: sessionId,
      message: message,
    });

    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || error.response?.data?.message || 'Failed to process message'
    );
  }
};

/**
 * Export video with burned subtitles
 * @param {string} sessionId - Video session ID
 * @param {string} filename - Optional output filename
 * @returns {Promise} Export response with download URL
 */
export const exportVideo = async (sessionId, filename = null) => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.EXPORT, {
      session_id: sessionId,
      filename: filename,
    });

    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || error.response?.data?.message || 'Failed to export video'
    );
  }
};

/**
 * Get video preview with current subtitles
 * @param {string} sessionId - Video session ID
 * @param {string} videoId - Video ID
 * @returns {Promise} Preview URL
 */
export const getVideoPreview = async (sessionId, videoId) => {
  try {
    const response = await apiClient.get(
      `${API_ENDPOINTS.PREVIEW}/${videoId}?session_id=${sessionId}`
    );

    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.message || 'Failed to get preview'
    );
  }
};

/**
 * Download file from URL
 * @param {string} url - File URL (relative or absolute)
 * @param {string} filename - Desired filename
 */
export const downloadFile = async (url, filename) => {
  try {
    // Construct full URL if it's a relative path
    const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;

    // Fetch the file as a blob to prevent navigation
    const response = await fetch(fullUrl);
    if (!response.ok) {
      throw new Error('Download failed');
    }

    const blob = await response.blob();

    // Create a blob URL and trigger download
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up the blob URL
    window.URL.revokeObjectURL(blobUrl);
  } catch (error) {
    console.error('Download error:', error);
    throw new Error('Failed to download file');
  }
};

export default apiClient;
