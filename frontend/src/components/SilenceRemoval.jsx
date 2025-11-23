import { useState } from 'react';
import { API_BASE_URL } from '../utils/constants';

const SilenceRemoval = ({ sessionId, silenceData, onSilenceRemoved }) => {
  const [isRemoving, setIsRemoving] = useState(false);
  const [error, setError] = useState(null);

  if (!silenceData || !silenceData.has_silence) {
    return null; // Don't show if no silence detected
  }

  const { stats, segments } = silenceData;

  const handleRemoveSilence = async () => {
    if (!sessionId) {
      setError('No session ID available');
      return;
    }

    setIsRemoving(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/remove-silence`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          noise_threshold: '-30dB',
          min_silence_duration: 1.0,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to remove silence');
      }

      const data = await response.json();
      console.log('Silence removed:', data);

      // Notify parent component
      if (onSilenceRemoved) {
        onSilenceRemoved(data);
      }
    } catch (err) {
      console.error('Error removing silence:', err);
      setError(err.message);
    } finally {
      setIsRemoving(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-amber-50 to-orange-50 border border-orange-200 rounded-xl p-5 shadow-sm">
      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center flex-shrink-0">
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M11 5L6 9H2v6h4l5 4V5z" />
            <path d="M23 9l-6 6" />
            <path d="M17 9l6 6" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-800 mb-1">
            Silence Detected
          </h3>
          <p className="text-sm text-gray-600">
            We found {stats.num_silent_segments} silent segment{stats.num_silent_segments !== 1 ? 's' : ''} in your video ({stats.total_silence_duration}s total, {stats.silence_percentage}%)
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-white rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {stats.num_silent_segments}
          </div>
          <div className="text-xs text-gray-600 mt-1">Segments</div>
        </div>
        <div className="bg-white rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {stats.total_silence_duration}s
          </div>
          <div className="text-xs text-gray-600 mt-1">Total Silence</div>
        </div>
        <div className="bg-white rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-orange-600">
            {stats.silence_percentage}%
          </div>
          <div className="text-xs text-gray-600 mt-1">Of Video</div>
        </div>
      </div>

      {/* Segments List (show max 3) */}
      {segments && segments.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-medium text-gray-700 mb-2">
            Silent segments:
          </p>
          <div className="bg-white rounded-lg p-3 max-h-24 overflow-y-auto text-xs text-gray-600">
            {segments.slice(0, 3).map((segment, index) => (
              <div key={index} className="mb-1">
                • {segment.start}s - {segment.end}s ({segment.duration}s)
              </div>
            ))}
            {segments.length > 3 && (
              <div className="text-gray-500 italic mt-1">
                ...and {segments.length - 3} more
              </div>
            )}
          </div>
        </div>
      )}

      {/* Action Button */}
      <button
        onClick={handleRemoveSilence}
        disabled={isRemoving}
        className={`
          w-full py-3 px-4 rounded-lg font-semibold text-white
          transition-all duration-200 flex items-center justify-center gap-2
          ${isRemoving
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 hover:-translate-y-0.5 hover:shadow-lg'
          }
        `}
      >
        {isRemoving ? (
          <>
            <svg
              className="animate-spin h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Removing Silence...
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
              <polyline points="16 16 12 12 8 16" />
              <line x1="12" y1="12" x2="12" y2="21" />
              <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
            </svg>
            Remove Silence ({stats.duration_after_removal}s final duration)
          </>
        )}
      </button>

      {/* Error Message */}
      {error && (
        <div className="mt-3 p-3 bg-red-100 border border-red-300 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Info */}
      <p className="mt-3 text-xs text-gray-500 text-center">
        This will create a new video without the silent parts
      </p>
    </div>
  );
};

export default SilenceRemoval;
