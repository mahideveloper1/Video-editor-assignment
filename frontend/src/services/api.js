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
 * @param {string} videoId - Video ID
 * @returns {Promise} Chat response
 */
export const sendChatMessage = async (sessionId, message, videoId) => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.CHAT, {
      session_id: sessionId,
      video_id: videoId,
      message: message,
    });

    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.message || 'Failed to process message'
    );
  }
};

/**
 * Export video with burned subtitles
 * @param {string} sessionId - Video session ID
 * @param {string} videoId - Video ID
 * @returns {Promise} Export response with download URL
 */
export const exportVideo = async (sessionId, videoId) => {
  try {
    const response = await apiClient.post(API_ENDPOINTS.EXPORT, {
      session_id: sessionId,
      video_id: videoId,
    });

    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.message || 'Failed to export video'
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
 * @param {string} url - File URL
 * @param {string} filename - Desired filename
 */
export const downloadFile = (url, filename) => {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export default apiClient;
