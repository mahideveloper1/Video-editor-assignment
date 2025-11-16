import { useRef, useState, useEffect } from 'react';
import { formatDuration } from '../utils/helpers';

const VideoPlayer = ({ videoUrl, subtitles = [], videoMetadata, showSubtitleOverlay = true }) => {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [currentSubtitle, setCurrentSubtitle] = useState(null);

  // Update current time
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);
    };

    const handleLoadedMetadata = () => {
      setDuration(video.duration);
    };

    const handleEnded = () => {
      setIsPlaying(false);
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('ended', handleEnded);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('ended', handleEnded);
    };
  }, []);

  // Update subtitle based on current time
  useEffect(() => {
    // Don't show subtitle overlay if showSubtitleOverlay is false (e.g., for preview/exported videos)
    if (!showSubtitleOverlay || !subtitles || subtitles.length === 0) {
      setCurrentSubtitle(null);
      return;
    }

    const activeSubtitle = subtitles.find((subtitle) => {
      const startTime = subtitle.start_time || subtitle.startTime || 0;
      const endTime = subtitle.end_time || subtitle.endTime || 0;
      return currentTime >= startTime && currentTime <= endTime;
    });

    setCurrentSubtitle(activeSubtitle || null);
  }, [currentTime, subtitles, showSubtitleOverlay]);

  const togglePlayPause = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e) => {
    const video = videoRef.current;
    if (!video) return;

    const seekTime = parseFloat(e.target.value);
    video.currentTime = seekTime;
    setCurrentTime(seekTime);
  };

  const handleVolumeChange = (e) => {
    const video = videoRef.current;
    if (!video) return;

    const newVolume = parseFloat(e.target.value);
    video.volume = newVolume;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isMuted) {
      video.volume = volume || 0.5;
      setIsMuted(false);
    } else {
      video.volume = 0;
      setIsMuted(true);
    }
  };

  const getSubtitleStyle = (subtitle) => {
    if (!subtitle) return {};

    return {
      fontFamily: subtitle.font_family || subtitle.fontFamily || 'Arial',
      fontSize: `${subtitle.font_size || subtitle.fontSize || 24}px`,
      color: subtitle.color || '#FFFFFF',
      backgroundColor: subtitle.background_color || subtitle.backgroundColor || 'rgba(0, 0, 0, 0.5)',
      padding: '8px 16px',
      borderRadius: '4px',
    };
  };

  if (!videoUrl) {
    return (
      <div className="w-full aspect-video bg-gray-800 rounded-xl flex items-center justify-center">
        <div className="text-center text-gray-500">
          <svg
            width="80"
            height="80"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mx-auto mb-5"
          >
            <polygon points="23 7 16 12 23 17 23 7" />
            <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
          </svg>
          <p className="text-lg font-semibold text-gray-400 mb-2">No video loaded</p>
          <span className="text-sm text-gray-600">Upload a video to get started</span>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-5xl mx-auto bg-black rounded-xl overflow-hidden shadow-lg">
      <div className="relative w-full bg-black" style={{ minHeight: '450px', maxHeight: '65vh' }}>
        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-full object-contain cursor-pointer"
          style={{ minHeight: '450px', maxHeight: '65vh' }}
          onClick={togglePlayPause}
        />

        {/* Subtitle Overlay */}
        {currentSubtitle && (
          <div
            className="absolute bottom-20 left-1/2 -translate-x-1/2 max-w-[80%] text-center font-semibold leading-snug pointer-events-none z-10 break-words"
            style={getSubtitleStyle(currentSubtitle)}
          >
            {currentSubtitle.text}
          </div>
        )}

        {/* Play/Pause Overlay */}
        {!isPlaying && (
          <div
            className="absolute inset-0 flex items-center justify-center bg-black/30 cursor-pointer transition-colors duration-200 hover:bg-black/50 z-[5]"
            onClick={togglePlayPause}
          >
            <div className="w-20 h-20 flex items-center justify-center bg-white/20 rounded-full transition-all duration-300 hover:bg-white/30 hover:scale-110">
              <svg
                width="64"
                height="64"
                viewBox="0 0 24 24"
                fill="white"
                stroke="white"
                strokeWidth="2"
              >
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
            </div>
          </div>
        )}
      </div>

      {/* Video Controls */}
      <div className="px-5 py-4 bg-gray-900">
        {/* Progress Bar */}
        <div className="mb-3">
          <input
            type="range"
            min="0"
            max={duration || 0}
            step="0.1"
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-1.5 bg-gray-700 rounded-sm outline-none cursor-pointer
              appearance-none
              [&::-webkit-slider-thumb]:appearance-none
              [&::-webkit-slider-thumb]:w-3.5
              [&::-webkit-slider-thumb]:h-3.5
              [&::-webkit-slider-thumb]:bg-primary
              [&::-webkit-slider-thumb]:rounded-full
              [&::-webkit-slider-thumb]:cursor-pointer
              [&::-webkit-slider-thumb]:transition-all
              [&::-webkit-slider-thumb]:hover:bg-primary-dark
              [&::-webkit-slider-thumb]:hover:scale-110
              [&::-moz-range-thumb]:w-3.5
              [&::-moz-range-thumb]:h-3.5
              [&::-moz-range-thumb]:bg-primary
              [&::-moz-range-thumb]:rounded-full
              [&::-moz-range-thumb]:cursor-pointer
              [&::-moz-range-thumb]:border-0
              [&::-moz-range-thumb]:transition-all
              [&::-moz-range-thumb]:hover:bg-primary-dark
              [&::-moz-range-thumb]:hover:scale-110"
          />
          <div className="flex gap-1.5 text-xs text-gray-400 mt-2 font-mono">
            <span>{formatDuration(currentTime)}</span>
            <span>/</span>
            <span>{formatDuration(duration)}</span>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={togglePlayPause}
              className="p-2 text-white bg-transparent border-0 cursor-pointer rounded flex items-center justify-center transition-all duration-200 hover:bg-white/10"
            >
              {isPlaying ? (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <rect x="6" y="4" width="4" height="16" />
                  <rect x="14" y="4" width="4" height="16" />
                </svg>
              ) : (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
              )}
            </button>

            <button
              onClick={toggleMute}
              className="p-2 text-white bg-transparent border-0 cursor-pointer rounded flex items-center justify-center transition-all duration-200 hover:bg-white/10"
            >
              {isMuted ? (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                  <line x1="23" y1="9" x2="17" y2="15" />
                  <line x1="17" y1="9" x2="23" y2="15" />
                </svg>
              ) : (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
                </svg>
              )}
            </button>

            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="w-20 h-1 bg-gray-700 rounded-sm outline-none cursor-pointer
                appearance-none
                [&::-webkit-slider-thumb]:appearance-none
                [&::-webkit-slider-thumb]:w-3
                [&::-webkit-slider-thumb]:h-3
                [&::-webkit-slider-thumb]:bg-white
                [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:cursor-pointer
                [&::-moz-range-thumb]:w-3
                [&::-moz-range-thumb]:h-3
                [&::-moz-range-thumb]:bg-white
                [&::-moz-range-thumb]:rounded-full
                [&::-moz-range-thumb]:cursor-pointer
                [&::-moz-range-thumb]:border-0"
            />
          </div>

          {videoMetadata && (
            <div className="text-sm text-gray-400">
              <span className="max-w-[200px] overflow-hidden text-ellipsis whitespace-nowrap inline-block">
                {videoMetadata.filename || 'Video'}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer;
