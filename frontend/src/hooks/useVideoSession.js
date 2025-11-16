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
    const sessionId = generateId();

    setSession({
      sessionId,
      videoId: videoData.videoId || videoData.video_id,
      videoUrl: videoData.videoUrl || videoData.video_url,
      videoFile: videoData.file,
      videoMetadata: videoData.metadata || {},
      subtitles: [],
      chatHistory: [],
      isProcessing: false,
      error: null,
    });

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
    setProcessing,
    setError,
    clearError,
    resetSession,
  };
};

export default useVideoSession;
