import { useState } from 'react';
import { exportVideo, downloadFile } from '../services/api';

const ExportButton = ({ sessionId, videoId, disabled = false, onExportSuccess, previewUrl = null }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(null);

  const handleExport = async () => {
    if (!sessionId || disabled) {
      alert('No video session found. Please upload a video first.');
      return;
    }

    setIsExporting(true);

    try {
      let response;
      let downloadUrl;
      let filename;

      // If we already have a preview, just download it
      if (previewUrl) {
        setExportProgress('Downloading...');
        downloadUrl = previewUrl;
        filename = `edited-video-${Date.now()}.mp4`;
      } else {
        // Generate export first
        setExportProgress('Preparing export...');
        response = await exportVideo(sessionId);

        setExportProgress('Processing video...');

        if (!response.download_url && !response.downloadUrl) {
          throw new Error('No download URL received from server');
        }

        setExportProgress('Export complete!');

        // Notify parent component about successful export (to update video player)
        if (onExportSuccess) {
          onExportSuccess(response);
        }

        downloadUrl = response.download_url || response.downloadUrl;
        filename = response.filename || `edited-video-${Date.now()}.mp4`;
      }

      // Extract the actual filename from the URL (e.g., /outputs/abc123_video.mp4 -> abc123_video.mp4)
      const urlFilename = downloadUrl.split('/').pop();

      // Use the dedicated download endpoint that forces download instead of playing
      const downloadEndpoint = `/api/download/${urlFilename}`;

      await downloadFile(downloadEndpoint, filename);

      setExportProgress('Downloaded!');
      setTimeout(() => {
        setExportProgress(null);
        setIsExporting(false);
      }, 1500);
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
            <span>{previewUrl ? 'Download Video' : 'Export & Download'}</span>
          </>
        )}
      </button>
    </div>
  );
};

export default ExportButton;
