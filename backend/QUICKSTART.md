# Quick Start Guide - AI Video Editor Backend

## 🚀 Phase 2 Complete - Video Processing Ready!

This guide will help you get the backend running quickly and test the video upload functionality.

## Prerequisites

1. **Python 3.10+** installed
2. **FFmpeg** installed (required for video processing)
3. **OpenAI API key** (for LLM features in Phase 3)

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

Verify:
```bash
ffmpeg -version
```

## Setup (5 minutes)

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create virtual environment
```bash
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create environment file
```bash
cp .env.example .env
```

Edit `.env` and add your API key (optional for now, required for Phase 3):
```env
OPENAI_API_KEY=sk-your-key-here
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

You should see:
```
🚀 Starting AI Video Editor API...
📦 Version: 1.0.0
🤖 LLM Provider: openai
🎯 Model: gpt-4o-mini
✓ Created directories:
  - Upload: /path/to/backend/uploads
  - Output: /path/to/backend/outputs
  - Temp: /path/to/backend/temp

INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Testing Phase 2 Features

### 1. Check API is running

Open browser: **http://localhost:8000**

You should see:
```json
{
  "message": "AI Video Editor API",
  "version": "1.0.0",
  "docs": "/api/docs",
  "health": "/api/health"
}
```

### 2. View API Documentation

Open: **http://localhost:8000/api/docs**

You'll see interactive Swagger UI with all endpoints.

### 3. Test Health Check

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-16T..."
}
```

### 4. Test Video Upload

**Using curl:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/path/to/your/video.mp4"
```

**Using Python:**
```python
import requests

url = "http://localhost:8000/api/upload"
files = {"file": open("video.mp4", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Response:**
```json
{
  "session_id": "sess_abc123456789",
  "filename": "video.mp4",
  "metadata": {
    "filename": "video.mp4",
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

**Save the `session_id` - you'll need it for next steps!**

### 5. Get Video Info

```bash
curl http://localhost:8000/api/video/sess_abc123456789
```

Response:
```json
{
  "session_id": "sess_abc123456789",
  "metadata": {...},
  "video_url": "/uploads/abc12345_video.mp4",
  "subtitle_count": 0,
  "created_at": "2025-11-16T..."
}
```

### 6. Delete Session (cleanup)

```bash
curl -X DELETE http://localhost:8000/api/video/sess_abc123456789
```

Response:
```json
{
  "message": "Session sess_abc123456789 deleted successfully"
}
```

## Testing with Frontend

### 1. Start backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### 2. Start frontend (in another terminal)
```bash
cd frontend
npm install
npm run dev
```

### 3. Open browser
Navigate to: **http://localhost:5173**

### 4. Upload a video
- Drag and drop a video file (MP4, MOV, AVI, WebM)
- Or click to browse and select a file
- Video should upload and display metadata!

## What Works Now (Phase 2)

✅ **Video Upload**
- Accept MP4, MOV, AVI, WebM
- Max 500MB
- File validation

✅ **Metadata Extraction**
- Duration, resolution, FPS
- Video codec information
- File size

✅ **Session Management**
- Create editing sessions
- Track video data
- Auto-cleanup after 1 hour

✅ **Video Services**
- FFmpeg integration
- Video validation
- Thumbnail generation
- Preview clip creation

✅ **Subtitle Services**
- SRT file generation
- ASS file generation (advanced styling)
- Subtitle validation
- Style management

## What's Coming in Phase 3

🔄 **LLM Integration**
- Chat-based subtitle editing
- Natural language prompting
- LangGraph workflow

🔄 **Export Functionality**
- Burn subtitles into video
- Download edited video

🔄 **Chat Interface**
- "Add subtitle 'Hello' from 0 to 5 seconds"
- "Change font to Arial, size 24, color red"
- Multiple edit rounds

## Troubleshooting

### FFmpeg not found
```bash
# Check FFmpeg installation
ffmpeg -version

# If not installed, install it:
# Ubuntu: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

### ModuleNotFoundError
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Port already in use
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### CORS errors from frontend
Check `.env` file:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### File upload fails
- Check file size (max 500MB)
- Check file format (MP4, MOV, AVI, WebM)
- Check disk space

## Development Tips

### Watch logs
The server shows detailed logs for all operations:
```
INFO:     127.0.0.1:52345 - "POST /api/upload HTTP/1.1" 201 Created
```

### Test with sample video
Download a sample video:
```bash
curl -o sample.mp4 "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"
```

### Interactive API testing
Use the Swagger UI: **http://localhost:8000/api/docs**
- Click "Try it out"
- Upload a file
- Execute
- See response

### Check uploaded files
```bash
ls -lh backend/uploads/
```

### Monitor sessions
Sessions auto-cleanup after 1 hour (configurable in `.env`)

## Next Steps

✅ Phase 1: Backend Foundation - **COMPLETE**
✅ Phase 2: Video Processing - **COMPLETE**
🔄 Phase 3: LLM Integration & Chat - **NEXT**
⏳ Phase 4: Export Functionality
⏳ Phase 5: Full Integration

Ready to continue with Phase 3? 🚀
