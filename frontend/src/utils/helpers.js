/**
 * Format file size to human readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Format duration to MM:SS format
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration
 */
export const formatDuration = (seconds) => {
  if (!seconds || isNaN(seconds)) return '00:00';

  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);

  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
};

/**
 * Validate video file
 * @param {File} file - File to validate
 * @param {Array} supportedFormats - Array of supported MIME types
 * @param {number} maxSize - Maximum file size in bytes
 * @returns {Object} Validation result
 */
export const validateVideoFile = (file, supportedFormats, maxSize) => {
  const errors = [];

  if (!file) {
    errors.push('No file selected');
    return { valid: false, errors };
  }

  if (!supportedFormats.includes(file.type)) {
    errors.push(`Unsupported file format. Supported formats: ${supportedFormats.join(', ')}`);
  }

  if (file.size > maxSize) {
    errors.push(`File size exceeds maximum limit of ${formatFileSize(maxSize)}`);
  }

  return {
    valid: errors.length === 0,
    errors,
  };
};

/**
 * Generate unique ID
 * @returns {string} Unique ID
 */
export const generateId = () => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Parse time string to seconds
 * @param {string} timeStr - Time string (e.g., "1:30", "90", "1m30s")
 * @returns {number} Time in seconds
 */
export const parseTimeToSeconds = (timeStr) => {
  if (!timeStr) return 0;

  // If it's already a number
  if (!isNaN(timeStr)) return parseFloat(timeStr);

  // Parse MM:SS format
  if (timeStr.includes(':')) {
    const parts = timeStr.split(':').map(p => parseInt(p, 10));
    if (parts.length === 2) {
      return parts[0] * 60 + parts[1];
    }
    if (parts.length === 3) {
      return parts[0] * 3600 + parts[1] * 60 + parts[2];
    }
  }

  return 0;
};
