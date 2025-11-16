import { MESSAGE_TYPES } from '../utils/constants';

const ChatMessage = ({ message }) => {
  const { type, content, timestamp } = message;

  const isUser = type === MESSAGE_TYPES.USER;
  const isAI = type === MESSAGE_TYPES.AI;
  const isSystem = type === MESSAGE_TYPES.SYSTEM;

  const formatTime = (date) => {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="flex gap-3 animate-slide-in">
      <div
        className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center
          ${isUser ? 'bg-primary text-white' : ''}
          ${isAI ? 'bg-secondary text-white' : ''}
          ${isSystem ? 'bg-warning text-white' : ''}
        `}
      >
        {isUser && (
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
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        )}
        {isAI && (
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
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
        )}
        {isSystem && (
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
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
        )}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-sm font-semibold text-gray-800">
            {isUser ? 'You' : isAI ? 'AI Assistant' : 'System'}
          </span>
          {timestamp && (
            <span className="text-xs text-gray-400">{formatTime(timestamp)}</span>
          )}
        </div>

        <div className="text-sm leading-relaxed text-gray-700 break-words">
          {content}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
