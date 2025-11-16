import { useState } from 'react';
import VideoUploader from './components/VideoUploader';
import VideoPlayer from './components/VideoPlayer';
import ChatInterface from './components/ChatInterface';
import PreviewButton from './components/PreviewButton';
import ExportButton from './components/ExportButton';
import { useVideoSession } from './hooks/useVideoSession';
import { sendChatMessage } from './services/api';
import { MESSAGE_TYPES } from './utils/constants';

function App() {
  const {
    session,
    initializeSession,
    addChatMessage,
    updateSubtitles,
    updateVideoUrl,
    setProcessing,
    setError,
    clearError,
  } = useVideoSession();

  const [showUploader, setShowUploader] = useState(true);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isShowingPreview, setIsShowingPreview] = useState(false);

  // Handle video upload success
  const handleUploadSuccess = (videoData) => {
    console.log('Video uploaded:', videoData);

    // Initialize session with video data
    initializeSession(videoData);

    // Hide uploader, show player
    setShowUploader(false);

    // Add system message
    addChatMessage({
      type: MESSAGE_TYPES.SYSTEM,
      content: `Video "${videoData.file?.name || 'video'}" uploaded successfully! You can now add subtitles using chat prompts.`,
      timestamp: new Date(),
    });
  };

  // Handle upload error
  const handleUploadError = (error) => {
    console.error('Upload error:', error);
    setError(error);
  };

  // Handle chat message send
  const handleSendMessage = async (message) => {
    if (!session.sessionId || !session.videoId) {
      alert('Please upload a video first.');
      return;
    }

    // Add user message to chat
    addChatMessage({
      type: MESSAGE_TYPES.USER,
      content: message,
      timestamp: new Date(),
    });

    // Set processing state
    setProcessing(true);
    clearError();

    try {
      // Send message to backend API
      const response = await sendChatMessage(
        session.sessionId,
        message,
        session.videoId
      );

      console.log('API Response:', response);

      // Add AI response to chat
      // Backend now returns message as an object with {type, content, timestamp, metadata}
      const aiContent = response.message?.content || response.message || response.response || 'Subtitle updated successfully!';

      addChatMessage({
        type: MESSAGE_TYPES.AI,
        content: aiContent,
        timestamp: new Date(),
      });

      // Update subtitles if provided
      if (response.subtitles) {
        updateSubtitles(response.subtitles);
        // Clear preview since subtitles changed
        setPreviewUrl(null);
        setIsShowingPreview(false);
      } else if (response.subtitle) {
        updateSubtitles(response.subtitle);
        // Clear preview since subtitles changed
        setPreviewUrl(null);
        setIsShowingPreview(false);
      }
    } catch (error) {
      console.error('Chat error:', error);

      // Add error message to chat
      addChatMessage({
        type: MESSAGE_TYPES.SYSTEM,
        content: `Error: ${error.message}`,
        timestamp: new Date(),
      });

      setError(error.message);
    } finally {
      setProcessing(false);
    }
  };

  // Handle preview ready
  const handlePreviewReady = (exportData) => {
    // Update video player to show preview with burned subtitles
    const exportedVideoUrl = `http://localhost:8000${exportData.download_url}`;
    updateVideoUrl(exportedVideoUrl);
    setPreviewUrl(exportData.download_url);
    setIsShowingPreview(true);

    // Add system message
    addChatMessage({
      type: MESSAGE_TYPES.SYSTEM,
      content: '✓ Preview ready! Review the video above. If satisfied, click "Download Video" to save it.',
      timestamp: new Date(),
    });
  };

  // Handle export success
  const handleExportSuccess = (exportData) => {
    // Update video player to show exported video with burned subtitles
    const exportedVideoUrl = `http://localhost:8000${exportData.download_url}`;
    updateVideoUrl(exportedVideoUrl);
    setPreviewUrl(exportData.download_url);
    setIsShowingPreview(true);

    // Add system message
    addChatMessage({
      type: MESSAGE_TYPES.SYSTEM,
      content: '✓ Video exported and downloaded successfully! You can continue editing or download again.',
      timestamp: new Date(),
    });
  };

  // Handle new upload (reset)
  const handleNewUpload = () => {
    setShowUploader(true);
    setPreviewUrl(null);
    setIsShowingPreview(false);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-purple-800 text-white px-8 py-5 shadow-md">
        <div className="max-w-[1800px] mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <svg
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polygon points="23 7 16 12 23 17 23 7" />
                <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold mb-1">AI Video Editor</h1>
              <p className="text-sm opacity-90">Chat-based subtitle editing</p>
            </div>
          </div>

          {session.videoId && (
            <button
              onClick={handleNewUpload}
              className="flex items-center gap-2 px-5 py-2.5 bg-white/20 border border-white/30 rounded-lg text-sm font-semibold hover:bg-white/30 transition-all duration-200 hover:-translate-y-0.5"
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 5v14M5 12h14" />
              </svg>
              New Video
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_450px] gap-6 px-8 py-6 max-w-[1800px] mx-auto w-full overflow-hidden">
        {/* Left Panel - Video */}
        <div className="flex flex-col gap-5 overflow-y-auto scrollbar-custom">
          {showUploader || !session.videoId ? (
            <div className="flex items-center justify-center min-h-[400px]">
              <VideoUploader
                onUploadSuccess={handleUploadSuccess}
                onUploadError={handleUploadError}
              />
            </div>
          ) : (
            <>
              <div className="bg-white rounded-xl overflow-hidden shadow-sm">
                <VideoPlayer
                  videoUrl={session.videoUrl}
                  subtitles={session.subtitles}
                  videoMetadata={session.videoMetadata}
                  showSubtitleOverlay={!isShowingPreview}
                />
              </div>

              {/* Preview & Export Buttons */}
              <div className="p-5 bg-white rounded-xl shadow-sm">
                <div className="flex flex-row gap-3">
                  {/* Preview Button */}
                  <PreviewButton
                    sessionId={session.sessionId}
                    disabled={!session.videoId || session.subtitles.length === 0}
                    onPreviewReady={handlePreviewReady}
                  />

                  {/* Download Button */}
                  <ExportButton
                    sessionId={session.sessionId}
                    videoId={session.videoId}
                    disabled={!session.videoId || session.subtitles.length === 0}
                    onExportSuccess={handleExportSuccess}
                    previewUrl={previewUrl}
                  />
                </div>
              </div>
            </>
          )}
        </div>

        {/* Right Panel - Chat */}
        <div className="flex flex-col overflow-hidden">
          <ChatInterface
            messages={session.chatHistory}
            onSendMessage={handleSendMessage}
            isProcessing={session.isProcessing}
            disabled={!session.videoId}
          />
        </div>
      </main>

      {/* Error Display */}
      {session.error && (
        <div className="fixed bottom-6 right-6 bg-red-400 text-white px-5 py-4 rounded-lg shadow-lg flex items-center gap-3 max-w-md z-50 animate-slide-up">
          <span>{session.error}</span>
          <button
            onClick={clearError}
            className="text-2xl leading-none opacity-80 hover:opacity-100 transition-opacity"
          >
            &times;
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
