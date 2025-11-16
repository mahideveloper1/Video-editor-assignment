import { useState } from 'react';
import { exportVideo } from '../services/api';

const PreviewButton = ({ sessionId, disabled = false, onPreviewReady }) => {
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [previewProgress, setPreviewProgress] = useState(null);

  const handlePreview = async () => {
    if (!sessionId || disabled) {
      alert('No video session found. Please upload a video first.');
      return;
    }

    setIsPreviewing(true);
    setPreviewProgress('Generating preview...');

    try {
      // Call export API to generate video with burned subtitles
      const response = await exportVideo(sessionId);

      setPreviewProgress('Preview ready!');

      // Check if we have a download URL
      if (response.download_url || response.downloadUrl) {
        // Notify parent component to update video player (but don't download)
        if (onPreviewReady) {
          onPreviewReady(response);
        }

        setTimeout(() => {
          setPreviewProgress(null);
          setIsPreviewing(false);
        }, 1500);
      } else {
        throw new Error('No preview URL received from server');
      }
    } catch (error) {
      console.error('Preview error:', error);
      alert(`Preview failed: ${error.message}`);
      setPreviewProgress(null);
      setIsPreviewing(false);
    }
  };

  return (
    <button
      onClick={handlePreview}
      disabled={disabled || isPreviewing}
      className={`
        w-full flex items-center justify-center gap-2.5 px-6 py-3.5 text-base font-semibold text-white
        border-0 rounded-xl cursor-pointer transition-all duration-300 outline-none
        ${isPreviewing
          ? 'bg-gradient-to-br from-blue-500 to-blue-700'
          : 'bg-gradient-to-br from-blue-600 to-blue-800 shadow-lg shadow-blue-600/40 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-blue-600/60'
        }
        disabled:bg-gray-300 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none
      `}
    >
      {isPreviewing ? (
        <>
          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          <span>{previewProgress || 'Generating...'}</span>
        </>
      ) : (
        <>
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <polygon points="10 8 16 12 10 16 10 8" />
          </svg>
          <span>Preview Video</span>
        </>
      )}
    </button>
  );
};

export default PreviewButton;
