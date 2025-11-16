"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class MessageType(str, Enum):
    """Message type for chat interface."""
    USER = "user"
    AI = "ai"
    SYSTEM = "system"


class SubtitlePosition(str, Enum):
    """Subtitle position on video."""
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


# Subtitle Models
class SubtitleStyle(BaseModel):
    """Subtitle styling configuration."""
    font_family: str = Field(default="Arial", description="Font family name")
    font_size: int = Field(default=32, ge=12, le=72, description="Font size in pixels")
    font_color: str = Field(default="white", description="Font color (name or hex)")
    position: SubtitlePosition = Field(default=SubtitlePosition.BOTTOM, description="Subtitle position")
    background_color: Optional[str] = Field(default=None, description="Background color (optional)")
    bold: bool = Field(default=False, description="Bold text")
    italic: bool = Field(default=False, description="Italic text")


class Subtitle(BaseModel):
    """Individual subtitle entry."""
    id: str = Field(description="Unique subtitle ID")
    text: str = Field(description="Subtitle text content")
    start_time: float = Field(ge=0, description="Start time in seconds")
    end_time: float = Field(ge=0, description="End time in seconds")
    style: SubtitleStyle = Field(description="Subtitle styling")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sub_123",
                "text": "Hello World",
                "start_time": 0.0,
                "end_time": 2.5,
                "style": {
                    "font_family": "Arial",
                    "font_size": 32,
                    "font_color": "white",
                    "position": "bottom"
                }
            }
        }


# Video Models
class VideoMetadata(BaseModel):
    """Video file metadata."""
    filename: str = Field(description="Original filename")
    duration: float = Field(ge=0, description="Video duration in seconds")
    width: int = Field(ge=1, description="Video width in pixels")
    height: int = Field(ge=1, description="Video height in pixels")
    fps: float = Field(ge=1, description="Frames per second")
    format: str = Field(description="Video format/codec")
    size: int = Field(ge=0, description="File size in bytes")


class VideoSession(BaseModel):
    """Video editing session."""
    session_id: str = Field(description="Unique session ID")
    video_path: str = Field(description="Path to uploaded video")
    metadata: VideoMetadata = Field(description="Video metadata")
    subtitles: List[Subtitle] = Field(default_factory=list, description="Current subtitles")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation time")


# Chat Models
class ChatMessage(BaseModel):
    """Chat message in conversation."""
    type: MessageType = Field(description="Message type")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ChatRequest(BaseModel):
    """Request to send a chat message."""
    session_id: str = Field(description="Video session ID")
    message: str = Field(min_length=1, max_length=2000, description="User message/prompt")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123",
                "message": "Add subtitle 'Hello World' from 0 to 5 seconds with red color"
            }
        }


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    session_id: str = Field(description="Video session ID")
    message: ChatMessage = Field(description="AI response message")
    subtitles: List[Subtitle] = Field(description="Updated subtitle list")
    preview_url: Optional[str] = Field(default=None, description="Preview URL if available")


# Upload Models
class UploadResponse(BaseModel):
    """Response from video upload."""
    session_id: str = Field(description="Created session ID")
    filename: str = Field(description="Uploaded filename")
    metadata: VideoMetadata = Field(description="Video metadata")
    message: str = Field(description="Success message")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123",
                "filename": "my_video.mp4",
                "metadata": {
                    "filename": "my_video.mp4",
                    "duration": 120.5,
                    "width": 1920,
                    "height": 1080,
                    "fps": 30.0,
                    "format": "mp4",
                    "size": 52428800
                },
                "message": "Video uploaded successfully"
            }
        }


# Export Models
class ExportRequest(BaseModel):
    """Request to export video with subtitles."""
    session_id: str = Field(description="Video session ID")
    filename: Optional[str] = Field(default=None, description="Output filename (optional)")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123",
                "filename": "my_edited_video.mp4"
            }
        }


class ExportResponse(BaseModel):
    """Response from export endpoint."""
    session_id: str = Field(description="Video session ID")
    download_url: str = Field(description="URL to download exported video")
    filename: str = Field(description="Exported filename")
    message: str = Field(description="Success message")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123",
                "download_url": "/api/download/sess_abc123_output.mp4",
                "filename": "my_edited_video.mp4",
                "message": "Video exported successfully"
            }
        }


# Error Models
class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    status_code: int = Field(description="HTTP status code")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid session",
                "detail": "Session sess_123 not found or expired",
                "status_code": 404
            }
        }


# Health Check
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy", description="Service status")
    version: str = Field(description="API version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Current time")
