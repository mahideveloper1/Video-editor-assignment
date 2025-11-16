import { useState } from 'react';
import { exportVideo, downloadFile } from '../services/api';

const ExportButton = ({ sessionId, videoId, disabled = false }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(null);

  const handleExport = async () => {
    if (!sessionId || !videoId || disabled) {
      alert('No video session found. Please upload a video first.');
      return;
    }

    setIsExporting(true);
    setExportProgress('Preparing export...');

    try {
      // Call export API
      const response = await exportVideo(sessionId, videoId);

      setExportProgress('Processing video...');

      // Check if we have a download URL
      if (response.download_url || response.downloadUrl) {
        setExportProgress('Download ready!');

        // Download the file
        const downloadUrl = response.download_url || response.downloadUrl;
        const filename = response.filename || `edited-video-${Date.now()}.mp4`;

        downloadFile(downloadUrl, filename);

        setTimeout(() => {
          setExportProgress(null);
          setIsExporting(false);
        }, 2000);
      } else {
        throw new Error('No download URL received from server');
      }
    } catch (error) {
      console.error('Export error:', error);
      alert(`Export failed: ${error.message}`);
      setExportProgress(null);
      setIsExporting(false);
    }
  };

  return (
    <div className="w-full">
      <button
        onClick={handleExport}
        disabled={disabled || isExporting}
        className={`
          w-full flex items-center justify-center gap-2.5 px-6 py-3.5 text-base font-semibold text-white
          border-0 rounded-xl cursor-pointer transition-all duration-300 outline-none
          ${isExporting
            ? 'bg-gradient-to-br from-secondary to-green-600'
            : 'bg-gradient-to-br from-purple-600 to-purple-800 shadow-lg shadow-purple-600/40 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-purple-600/60'
          }
          disabled:bg-gray-300 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none
        `}
      >
        {isExporting ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <span>{exportProgress || 'Exporting...'}</span>
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
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            <span>Export Video</span>
          </>
        )}
      </button>
    </div>
  );
};

export default ExportButton;
