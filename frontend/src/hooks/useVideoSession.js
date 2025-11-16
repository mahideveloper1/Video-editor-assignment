import { useState, useCallback } from 'react';
import { generateId } from '../utils/helpers';

/**
 * Custom hook for managing video editing session state
 */
export const useVideoSession = () => {
  const [session, setSession] = useState({
    sessionId: null,
    videoId: null,
    videoUrl: null,
    videoFile: null,
    videoMetadata: null,
    subtitles: [],
    chatHistory: [],
    isProcessing: false,
    error: null,
  });

  /**
   * Initialize new session with uploaded video
   */
  const initializeSession = useCallback((videoData) => {
    // IMPORTANT: Use session_id from backend, NOT generate a new one!
    const sessionId = videoData.session_id || videoData.sessionId;

    // Construct video URL from backend upload path
    const videoUrl = videoData.videoUrl
      || videoData.video_url
      || `http://localhost:8000/uploads/${videoData.metadata?.filename || videoData.filename}`;

    const sessionState = {
      sessionId,
      videoId: sessionId, // Use session ID as video ID (backend uses same ID)
      videoUrl,
      videoFile: videoData.file,
      videoMetadata: videoData.metadata || {},
      subtitles: [],
      chatHistory: [],
      isProcessing: false,
      error: null,
    };

    setSession(sessionState);

    // Save to sessionStorage for persistence across reloads
    sessionStorage.setItem('videoSession', JSON.stringify({
      sessionId,
      videoUrl,
      metadata: videoData.metadata || {}
    }));

    console.log('✓ Session initialized:', sessionId);

    return sessionId;
  }, []);

  /**
   * Add message to chat history
   */
  const addChatMessage = useCallback((message) => {
    setSession((prev) => ({
      ...prev,
      chatHistory: [...prev.chatHistory, message],
    }));
  }, []);

  /**
   * Update subtitles
   */
  const updateSubtitles = useCallback((newSubtitles) => {
    setSession((prev) => ({
      ...prev,
      subtitles: Array.isArray(newSubtitles)
        ? newSubtitles
        : [...prev.subtitles, newSubtitles],
    }));
  }, []);

  /**
   * Set processing state
   */
  const setProcessing = useCallback((isProcessing) => {
    setSession((prev) => ({
      ...prev,
      isProcessing,
    }));
  }, []);

  /**
   * Set error state
   */
  const setError = useCallback((error) => {
    setSession((prev) => ({
      ...prev,
      error,
      isProcessing: false,
    }));
  }, []);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setSession((prev) => ({
      ...prev,
      error: null,
    }));
  }, []);

  /**
   * Update video URL (for showing exported video)
   */
  const updateVideoUrl = useCallback((newVideoUrl) => {
    setSession((prev) => ({
      ...prev,
      videoUrl: newVideoUrl,
    }));
  }, []);

  /**
   * Reset session
   */
  const resetSession = useCallback(() => {
    setSession({
      sessionId: null,
      videoId: null,
      videoUrl: null,
      videoFile: null,
      videoMetadata: null,
      subtitles: [],
      chatHistory: [],
      isProcessing: false,
      error: null,
    });
  }, []);

  return {
    session,
    initializeSession,
    addChatMessage,
    updateSubtitles,
    updateVideoUrl,
    setProcessing,
    setError,
    clearError,
    resetSession,
  };
};

export default useVideoSession;
