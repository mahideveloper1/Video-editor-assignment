# AI Video Editor - Frontend

Chat-based video editing application with AI-powered subtitle generation and styling.

## Features

- 🎬 Video upload with drag-and-drop support
- 💬 Chat-based interface for editing commands
- 📝 Add and style subtitles using natural language prompts
- 🎨 Customize font family, size, and color
- 👁️ Real-time subtitle preview on video
- 💾 Export video with burned-in subtitles
- 🔄 Multi-round editing support

## Tech Stack

- **React 19** - UI library
- **Vite** - Build tool and dev server
- **Axios** - HTTP client for API calls
- **CSS3** - Styling with custom properties

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx      # Chat UI for prompts
│   │   ├── ChatMessage.jsx        # Individual message display
│   │   ├── VideoPlayer.jsx        # Video playback with subtitles
│   │   ├── VideoUploader.jsx      # File upload component
│   │   └── ExportButton.jsx       # Export final video
│   ├── services/
│   │   └── api.js                 # Backend API integration
│   ├── hooks/
│   │   └── useVideoSession.js     # Video state management
│   ├── utils/
│   │   ├── constants.js           # App constants
│   │   └── helpers.js             # Helper functions
│   ├── styles/                    # Component-specific styles
│   ├── App.jsx                    # Main app component
│   └── main.jsx                   # Entry point
├── .env.example                   # Environment variables template
└── package.json
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see backend README)

### Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your backend API URL:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

Built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Usage

### 1. Upload Video

- Drag and drop a video file or click to browse
- Supported formats: MP4, MOV, AVI, WebM
- Max file size: 500MB

### 2. Add Subtitles via Chat

Use natural language prompts to add and style subtitles:

**Adding Subtitles:**
```
"Add subtitle 'Hello World' from 0 to 5 seconds"
"Add subtitle 'Welcome' at 10 seconds"
```

**Styling Subtitles:**
```
"Change font to Arial, size 32, color red"
"Make the subtitle blue and bold"
"Set font size to 40px"
```

**Combined Commands:**
```
"Add subtitle 'Chapter 1' at 15 seconds in Arial, size 28, color #FF5733"
```

### 3. Export Video

Click the "Export Video" button to download the video with burned-in subtitles.

## Component Overview

### VideoUploader
- Drag-and-drop file upload
- File validation (format, size)
- Upload progress tracking
- Error handling

### VideoPlayer
- HTML5 video playback
- Custom controls (play/pause, seek, volume)
- Real-time subtitle overlay
- Responsive design

### ChatInterface
- Message history display
- Text input with keyboard shortcuts
- Example prompts for new users
- Processing state indication

### ChatMessage
- User/AI/System message types
- Timestamp display
- Metadata visualization (extracted parameters)
- Color-coded styling

### ExportButton
- One-click video export
- Progress indication
- Automatic file download

## API Integration

The frontend communicates with the backend via REST API:

### Endpoints

**Upload Video:**
```javascript
POST /api/upload
Content-Type: multipart/form-data
```

**Send Chat Message:**
```javascript
POST /api/chat
{
  "session_id": "string",
  "video_id": "string",
  "message": "string"
}
```

**Export Video:**
```javascript
POST /api/export
{
  "session_id": "string",
  "video_id": "string"
}
```

## State Management

Uses custom `useVideoSession` hook for managing:
- Video upload state
- Chat history
- Subtitle list
- Session information
- Processing state
- Error handling

## Styling

- CSS Modules for component styles
- Global CSS variables for theming
- Responsive design (mobile-friendly)
- Custom scrollbars
- Smooth animations and transitions

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Enhancements

- [ ] Undo/Redo functionality
- [ ] Subtitle timeline editor
- [ ] Video trimming
- [ ] Multiple subtitle tracks
- [ ] Preset style templates
- [ ] Keyboard shortcuts
- [ ] Dark mode
- [ ] Video format conversion

## Troubleshooting

### Video not playing
- Ensure video format is supported
- Check browser console for errors
- Verify video file is not corrupted

### Upload fails
- Check file size (max 500MB)
- Verify backend API is running
- Check network connection

### Subtitles not appearing
- Ensure subtitle timing is within video duration
- Check browser console for errors
- Verify API response contains subtitle data

## License

This project is part of an educational assignment.

## Support

For issues and questions, please refer to the main project README.
