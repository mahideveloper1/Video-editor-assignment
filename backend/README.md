# AI Video Editor - Backend

✅ **FULLY IMPLEMENTED** - Production Ready

FastAPI backend for AI-powered video editing with chat-based subtitle generation using LangGraph orchestration.

**Status**: All phases complete (Upload → Chat → Export)

## 📚 Documentation

- **[COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)** - Full usage guide with examples
- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup and testing
- **[test_workflow.py](test_workflow.py)** - Automated end-to-end tests

## Features

- **Video Upload**: Upload videos (MP4, MOV, AVI, WebM) up to 500MB
- **Chat-based Editing**: Natural language subtitle editing via LLM
- **LangGraph Orchestration**: Structured workflow for subtitle generation
- **Multiple Edit Rounds**: Cumulative subtitle edits in one session
- **Video Export**: Burn subtitles into video using FFmpeg
- **Session Management**: Track editing sessions with TTL
- **REST API**: Complete API for frontend integration

## Tech Stack

- **FastAPI**: Modern Python web framework
- **LangChain + LangGraph**: LLM orchestration
- **FFmpeg**: Video processing
- **Pydantic**: Data validation
- **OpenAI/Anthropic**: LLM providers
- **Uvicorn**: ASGI server

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── api/
│   │   ├── routes/
│   │   │   ├── upload.py       # Video upload endpoint
│   │   │   ├── chat.py         # Chat/subtitle editing endpoint
│   │   │   └── export.py       # Video export endpoint
│   ├── services/
│   │   ├── video_service.py    # Video processing with FFmpeg
│   │   ├── subtitle_service.py # Subtitle generation & SRT
│   │   └── llm_service.py      # LangGraph workflow
│   ├── models/
│   │   ├── schemas.py          # Pydantic models
│   │   └── state.py            # LangGraph state definitions
│   ├── utils/
│   │   ├── session.py          # Session management
│   │   └── helpers.py          # Utility functions
├── uploads/                     # Uploaded videos
├── outputs/                     # Exported videos
├── temp/                        # Temporary processing files
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

## Prerequisites

### System Requirements

1. **Python 3.10+**
   ```bash
   python --version
   ```

2. **FFmpeg**
   - **Ubuntu/Debian**:
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```
   - **macOS**:
     ```bash
     brew install ffmpeg
     ```
   - **Windows**:
     Download from [ffmpeg.org](https://ffmpeg.org/download.html)

   Verify installation:
   ```bash
   ffmpeg -version
   ```

3. **LLM API Key**
   - Get OpenAI API key: [platform.openai.com](https://platform.openai.com/api-keys)
   - Or Anthropic API key: [console.anthropic.com](https://console.anthropic.com/)

## Installation

### 1. Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use any text editor
```

**Required environment variables:**

```env
# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-key-here
LLM_MODEL=gpt-4o-mini

# Or for Anthropic:
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
# LLM_MODEL=claude-3-5-sonnet-20241022
```

### 4. Verify Installation

```bash
# Test FFmpeg
ffmpeg -version

# Test Python dependencies
python -c "import fastapi, langchain, langgraph; print('✓ All dependencies installed')"
```

## Running the Server

### Development Mode

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Python directly

```bash
python -m app.main
```

Server will start at: **http://localhost:8000**

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Upload Video
```bash
POST /api/upload
Content-Type: multipart/form-data

Form Data:
  - file: video file (MP4, MOV, AVI, WebM)

Response:
{
  "session_id": "sess_abc123",
  "filename": "video.mp4",
  "metadata": {...},
  "message": "Video uploaded successfully"
}
```

### Chat / Edit Subtitles
```bash
POST /api/chat
Content-Type: application/json

{
  "session_id": "sess_abc123",
  "message": "Add subtitle 'Hello World' from 0 to 5 seconds with red color"
}

Response:
{
  "session_id": "sess_abc123",
  "message": {...},
  "subtitles": [...],
  "preview_url": "/uploads/..."
}
```

### Export Video
```bash
POST /api/export
Content-Type: application/json

{
  "session_id": "sess_abc123",
  "filename": "my_video.mp4"
}

Response:
{
  "session_id": "sess_abc123",
  "download_url": "/outputs/...",
  "filename": "my_video.mp4",
  "message": "Video exported successfully"
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | AI Video Editor API |
| `DEBUG` | Debug mode | false |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:5173 |
| `LLM_PROVIDER` | LLM provider (openai/anthropic) | openai |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `LLM_MODEL` | Model name | gpt-4o-mini |
| `LLM_TEMPERATURE` | LLM temperature | 0.7 |
| `SESSION_TTL` | Session timeout (seconds) | 3600 |
| `DEFAULT_FONT_FAMILY` | Default font | Arial |
| `DEFAULT_FONT_SIZE` | Default font size | 32 |
| `DEFAULT_FONT_COLOR` | Default font color | white |

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Install dev dependencies
pip install black flake8 mypy

# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## Troubleshooting

### FFmpeg not found
```bash
# Verify FFmpeg installation
ffmpeg -version

# Install if missing (Ubuntu)
sudo apt install ffmpeg
```

### Import errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### CORS errors
- Check `CORS_ORIGINS` in `.env` matches frontend URL
- Default: `http://localhost:5173` for Vite

### LLM API errors
- Verify API key is correct in `.env`
- Check API quota/billing
- Ensure `LLM_PROVIDER` matches your key type

## Architecture

### LangGraph Workflow

The subtitle editing workflow uses LangGraph for structured LLM orchestration:

```
User Message → Parse Intent → Extract Parameters → Apply Edits → Generate Response
```

**Nodes:**
1. **Parse Intent**: Understand user request (add, modify, remove subtitle)
2. **Extract Parameters**: Get text, timing, styling (font, size, color)
3. **Apply Edits**: Update subtitle state
4. **Generate Response**: Create AI response

### Session Management

- In-memory session storage with TTL
- Automatic cleanup of expired sessions
- File cleanup on session deletion

### Video Processing

- FFmpeg for video metadata extraction
- SRT subtitle generation
- Subtitle burning into video

## Next Steps (Phase 2+)

- [ ] Implement video processing service
- [ ] Build LangGraph workflow
- [ ] Create API route handlers
- [ ] Add speech-to-text (Whisper) integration
- [ ] Database persistence (PostgreSQL/MongoDB)
- [ ] User authentication
- [ ] Rate limiting
- [ ] Docker deployment

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
