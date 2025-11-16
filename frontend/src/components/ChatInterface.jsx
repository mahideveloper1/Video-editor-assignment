import { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import { MESSAGE_TYPES } from '../utils/constants';

const ChatInterface = ({
  messages = [],
  onSendMessage,
  isProcessing = false,
  disabled = false
}) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();

    const trimmedValue = inputValue.trim();
    if (!trimmedValue || disabled || isProcessing) return;

    // Call parent callback
    if (onSendMessage) {
      onSendMessage(trimmedValue);
    }

    // Clear input
    setInputValue('');
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const examplePrompts = [
    'Add subtitle "Hello World" from 0 to 5 seconds',
    'Change font to Arial, size 32, color red',
    'Add subtitle "Welcome" at 10 seconds in blue',
    'Make the subtitle bold and larger',
  ];

  const handleExampleClick = (prompt) => {
    if (!disabled && !isProcessing) {
      setInputValue(prompt);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-sm overflow-hidden">
      {/* Chat Header */}
      <div className="px-6 py-5 border-b border-gray-200 bg-gray-50">
        <h2 className="text-xl font-bold text-gray-800 mb-1">Video Editor Assistant</h2>
        <p className="text-sm text-gray-600">Ask me to add or modify subtitles</p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-5 py-5 flex flex-col gap-4 scrollbar-custom">
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center text-gray-600 px-5 py-10">
            <div className="text-gray-300 mb-5">
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
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">Start a conversation</h3>
            <p className="text-sm text-gray-400 mb-8">Upload a video and use prompts to add or edit subtitles</p>

            <div className="w-full max-w-lg mt-5">
              <p className="text-sm font-semibold text-gray-700 mb-3 text-left">Try these examples:</p>
              {examplePrompts.map((prompt, index) => (
                <button
                  key={index}
                  className="w-full text-left px-4 py-3 mb-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-700 cursor-pointer transition-all duration-200 hover:bg-blue-50 hover:border-primary hover:text-blue-900 disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={() => handleExampleClick(prompt)}
                  disabled={disabled}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {isProcessing && (
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-9 h-9 bg-secondary rounded-full flex items-center justify-center text-white">
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
                </div>
                <div className="flex-1">
                  <div className="flex gap-1 p-3">
                    <span className="w-2 h-2 bg-secondary rounded-full animate-typing"></span>
                    <span className="w-2 h-2 bg-secondary rounded-full animate-typing [animation-delay:0.2s]"></span>
                    <span className="w-2 h-2 bg-secondary rounded-full animate-typing [animation-delay:0.4s]"></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="px-5 py-4 border-t border-gray-200 bg-white">
        <form onSubmit={handleSubmit} className="flex gap-3 items-end">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              disabled
                ? 'Upload a video first to start editing...'
                : 'Type your prompt here... (e.g., "Add subtitle Hello at 5 seconds")'
            }
            disabled={disabled || isProcessing}
            className="flex-1 px-4 py-3 text-sm leading-6 border border-gray-200 rounded-lg resize-none max-h-32 font-inherit transition-colors duration-200 focus:outline-none focus:border-primary disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed"
            rows="1"
          />
          <button
            type="submit"
            disabled={disabled || isProcessing || !inputValue.trim()}
            className="flex-shrink-0 w-11 h-11 flex items-center justify-center bg-primary text-white border-0 rounded-lg cursor-pointer transition-all duration-200 outline-none hover:bg-primary-dark hover:-translate-y-0.5 hover:shadow-lg hover:shadow-primary/40 disabled:bg-gray-300 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
          >
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
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </form>
        <div className="mt-2 text-xs text-gray-400 text-center">
          Press <kbd className="px-1.5 py-0.5 bg-gray-200 rounded text-xs font-mono">Enter</kbd> to send, <kbd className="px-1.5 py-0.5 bg-gray-200 rounded text-xs font-mono">Shift + Enter</kbd> for new line
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
