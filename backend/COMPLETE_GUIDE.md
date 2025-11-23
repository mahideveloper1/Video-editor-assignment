# AI Video Editor - Complete Guide

## 🎬 Full-Stack Chat-Based Video Editor

A complete FastAPI + React application for AI-powered video subtitle editing using natural language.

---

## ✨ Features

### ✅ Fully Implemented

- **Video Upload**: Drag-and-drop upload (MP4, MOV, AVI, WebM) up to 500MB
- **AI Chat Interface**: Natural language subtitle editing powered by LangGraph
- **Real-time Preview**: See subtitles on video player
- **Style Customization**: Font, size, color, position, bold, italic
- **Multiple Rounds**: Edit subtitles across multiple chat interactions
- **Video Export**: Burn subtitles into video with FFmpeg
- **Session Management**: Auto-cleanup after 1 hour
- **Full API**: Complete REST API with Swagger docs

---

## 🚀 Quick Start (5 minutes)

### Prerequisites

1. **Python 3.10+**
2. **Node.js 18+** (for frontend)
3. **FFmpeg** installed
4. **OpenAI API Key** or **Anthropic API Key**

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Verify:**
```bash
ffmpeg -version
```

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Add your API key

# 5. Start server
uvicorn app.main:app --reload
```

Server runs at: **http://localhost:8000**

### Frontend Setup

```bash
# 1. Navigate to frontend (in new terminal)
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment
cp .env.example .env

# 4. Start dev server
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## 📖 Usage Guide

### Step 1: Upload Video

1. Open http://localhost:5173
2. Drag and drop a video file (or click to browse)
3. Wait for upload to complete
4. Video player will appear with metadata

### Step 2: Add Subtitles via Chat

Type natural language commands in the chat:

**Basic Examples:**
```
Add subtitle "Hello World!" from 0 to 5 seconds
Add "Welcome!" from 1:30 to 1:35
Add subtitle "Chapter 1" at 10 seconds for 5 seconds
```

**With Styling:**
```
Add "Important!" from 5 to 8 seconds with red color
Add subtitle "Title" from 0 to 3 seconds, size 48, bold
Add "The End" from 2:00 to 2:10 with yellow color, Arial font
Add subtitle "Warning" from 15 to 20 seconds, red, size 36, bold, italic
```

**Advanced Examples:**
```
Add "Introduction" from 0 to 5 seconds with white color, Helvetica font, size 42, bold, position top
Add subtitle "Conclusion" from 1 minute to 1:05 with #FF5733 color
```

### Step 3: Preview

- Subtitles appear instantly on video player
- Play video to see timing
- Adjust timing via new chat messages

### Step 4: Export

1. Click "Export Video" button
2. Wait for processing (may take 1-2 minutes)
3. Download final video with burned subtitles

---

## 🎨 Styling Options

### Colors

**Color Names:**
```
red, blue, yellow, white, green, black, orange, purple, pink, cyan, magenta
```

**Hex Codes:**
```
#FF0000 (red), #00FF00 (green), #0000FF (blue), #FFFF00 (yellow)
```

### Fonts

```
Arial, Helvetica, Roboto, Times New Roman, Courier, Verdana, Georgia
```

### Sizes

```
12-72 pixels (default: 32)
```

### Position

```
top, center, bottom (default: bottom)
```

### Text Styles

```
bold, italic
```

---

## 🔧 API Reference

### Health Check

```bash
GET /api/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Upload Video

```bash
POST /api/upload
Content-Type: multipart/form-data

curl -X POST "http://localhost:8000/api/upload" \
     -F "file=@video.mp4"
```

Response:
```json
{
  "session_id": "sess_abc123",
  "filename": "video.mp4",
  "metadata": {
    "duration": 120.5,
    "width": 1920,
    "height": 1080,
    "fps": 30.0,
    "format": "mp4 (h264)",
    "size": 52428800
  },
  "message": "Video uploaded successfully"
}
```

### Chat / Add Subtitles

```bash
POST /api/chat
Content-Type: application/json

curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "sess_abc123",
       "message": "Add subtitle Hello World from 0 to 5 seconds with red color"
     }'
```

Response:
```json
{
  "session_id": "sess_abc123",
  "message": {
    "type": "ai",
    "content": "✓ Added subtitle: \"Hello World\" from 0.0s to 5.0s with color: red",
    "metadata": {
      "text": "Hello World",
      "start_time": 0.0,
      "end_time": 5.0,
      "font_color": "red"
    }
  },
  "subtitles": [...],
  "preview_url": "/uploads/..."
}
```

### Get Subtitles

```bash
GET /api/subtitles/{session_id}

curl "http://localhost:8000/api/subtitles/sess_abc123"
```

### Export Video

```bash
POST /api/export
Content-Type: application/json

curl -X POST "http://localhost:8000/api/export" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "sess_abc123",
       "filename": "my_video.mp4"
     }'
```

Response:
```json
{
  "session_id": "sess_abc123",
  "download_url": "/outputs/abc123_my_video.mp4",
  "filename": "my_video.mp4",
  "message": "Video exported successfully with subtitles"
}
```

### Download Video

```bash
GET /api/download/{filename}

curl -O "http://localhost:8000/api/download/abc123_my_video.mp4"
```

### Chat History

```bash
GET /api/chat/history/{session_id}

curl "http://localhost:8000/api/chat/history/sess_abc123"
```

### Clear Subtitles

```bash
DELETE /api/subtitles/{session_id}

curl -X DELETE "http://localhost:8000/api/subtitles/sess_abc123"
```

---

## 🧪 Testing

### Automated Tests

```bash
# Run test script (without video upload)
python test_workflow.py

# Run with video upload
python test_workflow.py /path/to/video.mp4
```

### Manual Testing with curl

**1. Health Check:**
```bash
curl http://localhost:8000/api/health
```

**2. Upload Video:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
     -F "file=@test_video.mp4"
# Save the session_id from response
```

**3. Add Subtitle:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "sess_YOUR_SESSION_ID",
       "message": "Add subtitle Hello World from 0 to 5 seconds with red color"
     }'
```

**4. Export:**
```bash
curl -X POST "http://localhost:8000/api/export" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "sess_YOUR_SESSION_ID"
     }'
```

### Interactive API Docs

Open: **http://localhost:8000/api/docs**

- Click "Try it out" on any endpoint
- Fill in parameters
- Execute
- See response

---

## 🏗️ Architecture

### Backend (FastAPI + LangGraph)

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── api/routes/          # API endpoints
│   │   ├── upload.py        # Video upload
│   │   ├── chat.py          # Chat interface
│   │   └── export.py        # Export video
│   ├── services/
│   │   ├── video_service.py   # FFmpeg operations
│   │   ├── subtitle_service.py # SRT/ASS generation
│   │   └── llm_service.py     # LangGraph workflow
│   ├── models/
│   │   ├── schemas.py       # Pydantic models
│   │   └── state.py         # LangGraph state
│   └── utils/
│       ├── session.py       # Session management
│       └── helpers.py       # Utilities
```

### Frontend (React + Vite)

```
frontend/
├── src/
│   ├── components/
│   │   ├── VideoUploader.jsx    # Upload UI
│   │   ├── VideoPlayer.jsx      # Video + subtitles
│   │   ├── ChatInterface.jsx    # Chat UI
│   │   └── ExportButton.jsx     # Export button
│   ├── services/
│   │   └── api.js              # API client
│   └── hooks/
│       └── useVideoSession.js  # State management
```

### LangGraph Workflow

```
User Message
    ↓
Parse Intent (add/modify/remove)
    ↓
Extract Parameters (text, time, style)
    ↓
Apply Edits (update subtitle state)
    ↓
Generate Response (AI message)
    ↓
Return Updated Subtitles
```

---

## 🔐 Environment Variables

### Backend (.env)

```env
# LLM Configuration
LLM_PROVIDER=openai              # or "anthropic"
OPENAI_API_KEY=sk-xxx           # Your OpenAI key
LLM_MODEL=gpt-4o-mini           # or gpt-4o, gpt-3.5-turbo

# For Anthropic:
# ANTHROPIC_API_KEY=sk-ant-xxx
# LLM_MODEL=claude-3-5-sonnet-20241022

# Server
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# File Settings
MAX_UPLOAD_SIZE=524288000       # 500MB
SESSION_TTL=3600                # 1 hour

# Defaults
DEFAULT_FONT_FAMILY=Arial
DEFAULT_FONT_SIZE=32
DEFAULT_FONT_COLOR=white
DEFAULT_SUBTITLE_POSITION=bottom

# Video Quality
VIDEO_QUALITY=high              # high, medium, low
FFMPEG_THREADS=4
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🐛 Troubleshooting

### Server won't start

**Error: FFmpeg not found**
```bash
# Install FFmpeg
sudo apt install ffmpeg  # Ubuntu
brew install ffmpeg      # macOS
```

**Error: ModuleNotFoundError**
```bash
# Activate venv and reinstall
source venv/bin/activate
pip install -r requirements.txt
```

### API errors

**Error: "OpenAI API key not configured"**
```bash
# Edit .env and add:
OPENAI_API_KEY=sk-your-actual-key
```

**Error: "Session not found"**
- Sessions expire after 1 hour (configurable)
- Upload a new video to create a new session

### Upload fails

**Error: "File too large"**
- Max size: 500MB (configurable in .env)
- Compress your video first

**Error: "Invalid file format"**
- Supported: MP4, MOV, AVI, WebM
- Convert to MP4 for best compatibility

### Export fails

**Error: "No subtitles to export"**
- Add subtitles via chat first

**Error: "FFmpeg error"**
- Check FFmpeg is installed: `ffmpeg -version`
- Check video file is not corrupted

### CORS errors

**Error: "CORS policy blocked"**
- Check `CORS_ORIGINS` in backend/.env includes frontend URL
- Default: `http://localhost:5173`

---

## 📊 Performance Tips

### Video Processing

- **Use high quality** for final export (slower)
- **Use medium quality** for testing (balanced)
- **Use low quality** for quick previews (faster)

Configure in .env:
```env
VIDEO_QUALITY=medium
```

### Session Cleanup

Sessions auto-cleanup after TTL. Adjust as needed:
```env
SESSION_TTL=7200  # 2 hours
```

### FFmpeg Threads

More threads = faster processing (but more CPU):
```env
FFMPEG_THREADS=8  # Use 8 CPU cores
```

---

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
# Dockerfile coming soon
```

### Manual Deployment

**Backend:**
```bash
# Use production ASGI server
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend:**
```bash
npm run build
# Serve dist/ with nginx or static hosting
```

---

## 📝 Development

### Adding New Features

**1. Add new subtitle intent:**
- Update `llm_service.py` -> `_parse_intent_node`
- Add handler in `_extract_parameters_node`

**2. Add new styling option:**
- Update `SubtitleStyle` in `schemas.py`
- Update subtitle generation in `subtitle_service.py`

**3. Add new API endpoint:**
- Create route in `app/api/routes/`
- Import in `main.py`

### Code Quality

```bash
# Format
black app/

# Lint
flake8 app/

# Type check
mypy app/

# Test
pytest
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

MIT License

---

## 🆘 Support

- **Issues**: GitHub Issues
- **Docs**: http://localhost:8000/api/docs (when running)
- **Examples**: See `test_workflow.py`

---

## 🎉 Success!

Your AI Video Editor is ready! Start by:

1. ✅ Starting backend: `uvicorn app.main:app --reload`
2. ✅ Starting frontend: `npm run dev`
3. ✅ Opening http://localhost:5173
4. ✅ Uploading a video
5. ✅ Adding subtitles via chat
6. ✅ Exporting your video!

Enjoy! 🎬✨
