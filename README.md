# AI Video Editor

✅ **FULLY IMPLEMENTED** - Full-Stack AI-Powered Chat-Based Video Subtitle Editor

A complete full-stack application for intelligent video subtitle editing using natural language. Built with **FastAPI**, **React 19**, **LangGraph**, **Google Gemini AI**, and **FFmpeg**.

![Status](https://img.shields.io/badge/status-complete-success)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/frontend-React_19-61DAFB)
![AI](https://img.shields.io/badge/AI-Gemini_+_LangGraph-7B68EE)

---

## 🎥 About

AI Video Editor revolutionizes subtitle editing by allowing you to use natural language instead of manual timing and styling. Simply chat with the AI - "add 'Hello World' at 5 seconds in red color" - and watch as it handles all the technical details.

The application features real-time preview, multi-round editing, and exports professional videos with permanently burned-in subtitles.

---

## ✨ Key Features

### 🤖 Intelligent Chat-Based Editing
- **Natural Language Commands**: "Add 'Hello' at 5 seconds with red color, size 48"
- **Context-Aware**: "Make the previous subtitle blue"
- **Smart Modification**: Edit existing subtitles by referencing them
- **Flexible Time Parsing**: Supports "5 seconds", "1:30", "2 minutes", etc.

### 🎨 Advanced Subtitle Styling
- **Colors**: Named colors (red, blue, yellow) or hex codes (#FF0000)
- **Fonts**: Arial, Helvetica, Roboto, Times New Roman, and more
- **Sizes**: 12-72 pixels
- **Position**: Top, center, or bottom
- **Styles**: Bold, italic, or combinations

### 👁️ Real-Time Preview & Export
- **Live Preview**: See subtitles overlaid on video instantly
- **Separate Preview Button**: Generate and review video before downloading
- **Smart Export**: Download only when satisfied with results
- **Multi-Round Editing**: Continue editing and re-exporting the same video

### 🔄 Intelligent Subtitle Modification
- **Reference Previous Subtitles**: "Make the last subtitle red"
- **Index-Based Editing**: "Change subtitle 1 to size 48"
- **Contextual Understanding**: AI knows which subtitle you're referring to
- **Partial Updates**: Only changes what you specify, keeps the rest

### 🎯 User-Friendly Interface
- **Drag & Drop Upload**: Simple video upload interface
- **Clean Chat UI**: Spacious text input with visual feedback
- **Responsive Video Player**: Adapts to screen size with visible controls
- **Side-by-Side Actions**: Preview and Download buttons for clear workflow

---

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **FFmpeg** - Video processing library
- **Google Gemini API Key** - [Get API Key](https://makersuite.google.com/app/apikey) 

### 1. Clone Repository

```bash
git https://github.com/mahideveloper1/Video-editor-assignment
cd Video-editor-assignment
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment

Create a `.env` file in the `backend` directory:

```env
# backend/.env

# LLM Configuration
LLM_PROVIDER=google
GOOGLE_API_KEY=your_api_key
LLM_MODEL=gemini-2.0-flash-lite / whatever you prefer
LLM_TEMPERATURE=0.7
```

#### Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

### 3. Frontend Setup

#### Install Dependencies

```bash
cd ../frontend
npm install
```

#### Configure Environment (Optional)

Create `.env` file in the `frontend` directory if you need custom API URL:

```env
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```

#### Start Development Server

```bash
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### 4. Verify Installation

1. **Check FFmpeg**: Run `ffmpeg -version` in terminal
2. **Test Backend**: Visit http://localhost:8000/docs
3. **Test Frontend**: Visit http://localhost:5173
4. **Upload a video** and try adding a subtitle!

---

## 📖 Usage Guide

### Basic Workflow

#### 1. Upload Video
```
- Click upload area or drag & drop a video file
- Supported formats: MP4, AVI, MOV, MKV, WEBM
- Max file size: 500MB
- Video metadata extracted automatically
```

#### 2. Add Subtitles via Chat

**Simple Examples:**
```
"Add subtitle 'Hello World' from 0 to 5 seconds"
"Add 'Welcome!' at 10 seconds with red color"
"Add 'Chapter 1' from 1:30 to 1:35, size 48, bold"
```

**Advanced Examples:**
```
"Add 'The End' from 2 minutes to 2:10 with yellow color, Arial font, position top"
"Add subtitle 'Important!' at 30 seconds, size 36, red, bold, italic"
```

#### 3. Modify Existing Subtitles

**Reference by Position:**
```
"Make the previous subtitle red"
"Change the last subtitle to blue"
"Make the last one bigger"
```

**Reference by Index:**
```
"Make subtitle 1 bigger"
"Change subtitle 2 to size 48"
"Change the first subtitle to yellow"
```

#### 4. Preview Video
```
- Click "Preview Video" button
- Video generates with burned-in subtitles
- Review in video player
- Make more edits if needed
```

#### 5. Download Video
```
- Click "Download Video" button
- Video downloads with all subtitles permanently burned in
- Continue editing or start a new session
```

### Advanced Features

#### Time Format Options
```
Seconds:           "5 seconds", "10s", "15"
Minutes:Seconds:   "1:30", "2:45", "0:30"
Full Format:       "2 minutes 30 seconds"
Hours:Min:Sec:     "1:30:45"
```

#### Color Options
```
Named Colors:  red, blue, green, yellow, white, black, orange, purple, pink
Hex Codes:     #FF0000, #00FF00, #0000FF, #FFFF00
RGB:           rgb(255, 0, 0)
```

#### Font Options
```
Common Fonts:  Arial, Helvetica, Roboto, Times New Roman
System Fonts:  Georgia, Verdana, Courier New, Comic Sans MS
Custom:        Any font name installed on the system
```

#### Styling Options
```
Size:      12-72 pixels (e.g., "size 48")
Position:  top, center, bottom
Bold:      "bold" or "make it bold"
Italic:    "italic" or "make it italic"
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React 19)                      │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │VideoUploader │  │VideoPlayer   │  │ChatInterface │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │PreviewButton │  │ExportButton  │                            │
│  └──────────────┘  └──────────────┘                            │
└────────────────────────┬───────────────────────────────────────┘
                         │ REST API (Axios)
┌────────────────────────▼───────────────────────────────────────┐
│                   BACKEND (FastAPI + Python)                    │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │Upload Route  │  │Chat Route    │  │Export Route  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         │       ┌──────────▼──────────┐      │                  │
│         │       │  LangGraph Workflow  │      │                  │
│         │       │  ┌────────────────┐ │      │                  │
│         │       │  │ Parse Intent   │ │      │                  │
│         │       │  └────────┬───────┘ │      │                  │
│         │       │  ┌────────▼───────┐ │      │                  │
│         │       │  │Extract Params  │ │      │                  │
│         │       │  └────────┬───────┘ │      │                  │
│         │       │  ┌────────▼───────┐ │      │                  │
│         │       │  │ Apply Edits    │ │      │                  │
│         │       │  └────────┬───────┘ │      │                  │
│         │       │  ┌────────▼───────┐ │      │                  │
│         │       │  │Generate Reply  │ │      │                  │
│         │       │  └────────────────┘ │      │                  │
│         │       └─────────────────────┘      │                  │
│         │                  │                  │                  │
│  ┌──────▼──────────────────▼──────────────────▼───────┐         │
│  │              Services Layer                        │         │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │         │
│  │  │  Video   │ │ Subtitle │ │ Session  │          │         │
│  │  │ Service  │ │ Service  │ │ Manager  │          │         │
│  │  │(FFmpeg)  │ │(SRT/ASS) │ │(Memory)  │          │         │
│  │  └──────────┘ └──────────┘ └──────────┘          │         │
│  └───────────────────────────────────────────────────┘         │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Google Gemini API    │
              │  (gemini-1.5-flash)   │
              └──────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
- **React 19** - Latest UI framework with improved features
- **Vite** - Lightning-fast build tool and dev server
- **Tailwind CSS 4** - Utility-first CSS framework
- **Axios** - Promise-based HTTP client

### Backend
- **FastAPI** - Modern, high-performance Python web framework
- **LangGraph** - State machine for LLM workflow orchestration
- **LangChain** - Framework for developing LLM applications
- **Google Gemini 1.5 Flash** - Fast, efficient AI language model
- **FFmpeg** - Complete video processing solution
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - Lightning-fast ASGI server

### Infrastructure
- **FFmpeg** - Video encoding, subtitle burning
- **Python 3.9+** - Backend runtime
- **Node.js 18+** - Frontend runtime

---

