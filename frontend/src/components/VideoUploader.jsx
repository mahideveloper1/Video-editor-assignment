import { useState, useRef } from 'react';
import {
  SUPPORTED_VIDEO_FORMATS,
  SUPPORTED_VIDEO_EXTENSIONS,
  MAX_FILE_SIZE,
} from '../utils/constants';
import { validateVideoFile, formatFileSize } from '../utils/helpers';
import { uploadVideo } from '../services/api';

const VideoUploader = ({ onUploadSuccess, onUploadError }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = (file) => {
    // Validate file
    const validation = validateVideoFile(
      file,
      SUPPORTED_VIDEO_FORMATS,
      MAX_FILE_SIZE
    );

    if (!validation.valid) {
      const errorMessage = validation.errors.join(', ');
      if (onUploadError) {
        onUploadError(errorMessage);
      }
      alert(errorMessage);
      return;
    }

    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const response = await uploadVideo(selectedFile, (progress) => {
        setUploadProgress(progress);
      });

      // Success
      if (onUploadSuccess) {
        onUploadSuccess({
          ...response,
          file: selectedFile,
        });
      }

      // Reset
      setSelectedFile(null);
      setUploadProgress(0);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Upload error:', error);
      if (onUploadError) {
        onUploadError(error.message);
      }
      alert(`Upload failed: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleCancelSelection = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full p-5">
      {!selectedFile ? (
        <div
          className={`
            border-2 border-dashed rounded-xl px-10 py-15 text-center cursor-pointer
            transition-all duration-300 bg-gray-50
            ${isDragging
              ? 'border-blue-600 bg-blue-50 scale-105'
              : 'border-gray-300 hover:border-primary hover:bg-blue-50'
            }
          `}
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleBrowseClick}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={SUPPORTED_VIDEO_EXTENSIONS.join(',')}
            onChange={handleFileInputChange}
            className="hidden"
          />

          <div className="text-primary mb-5 flex justify-center">
            <svg
              width="64"
              height="64"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>

          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            Drop your video here
          </h3>
          <p className="text-sm text-gray-600 mb-5">or click to browse</p>

          <div className="mt-5 pt-5 border-t border-gray-200">
            <p className="text-xs text-gray-500 font-medium mb-1">
              Supported formats: {SUPPORTED_VIDEO_EXTENSIONS.join(', ')}
            </p>
            <p className="text-xs text-gray-400">
              Max size: {formatFileSize(MAX_FILE_SIZE)}
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl p-8">
          <div className="flex items-center gap-5 mb-6">
            <div className="text-primary flex-shrink-0">
              <svg
                width="48"
                height="48"
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

            <div className="flex-1 min-w-0">
              <h4 className="text-base font-semibold text-gray-800 mb-1 break-words">
                {selectedFile.name}
              </h4>
              <p className="text-sm text-gray-600">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
          </div>

          {isUploading ? (
            <div className="mt-5">
              <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden mb-3">
                <div
                  className="h-full bg-gradient-to-r from-primary to-blue-600 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-sm text-primary font-semibold text-center">
                {uploadProgress}% uploaded
              </p>
            </div>
          ) : (
            <div className="flex gap-3 justify-center mt-5">
              <button
                className="px-6 py-3 text-sm font-semibold text-black bg-primary rounded-lg
                  hover:bg-primary-dark hover:-translate-y-0.5 hover:shadow-lg hover:shadow-primary/40
                  transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                  disabled:transform-none"
                onClick={handleUpload}
                disabled={isUploading}
              >
                Upload Video
              </button>
              <button
                className="px-6 py-3 text-sm font-semibold text-gray-800 bg-gray-200 rounded-lg
                  hover:bg-gray-300 transition-all duration-200 disabled:opacity-50
                  disabled:cursor-not-allowed"
                onClick={handleCancelSelection}
                disabled={isUploading}
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoUploader;
