"""
Chat API endpoint for subtitle editing via natural language.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from pathlib import Path

from app.config import settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    MessageType,
    Subtitle,
    ErrorResponse
)
from app.services.llm_service import llm_service
from app.utils.session import session_manager


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Send a chat message to edit subtitles using natural language.

    This endpoint uses AI (powered by LangGraph) to understand your subtitle editing requests.

    **Examples:**
    - "Add subtitle 'Hello World' from 0 to 5 seconds"
    - "Add 'Welcome!' from 1:30 to 1:35 with red color"
    - "Add subtitle 'Chapter 1' at 10 seconds for 5 seconds, size 48, bold"
    - "Add 'The End' from 2 minutes to 2:10 with yellow color, Arial font"

    **Supported styling:**
    - **Colors**: red, blue, yellow, white, green, black, or hex codes (#FF0000)
    - **Fonts**: Arial, Helvetica, Roboto, Times New Roman, etc.
    - **Sizes**: 12-72 pixels
    - **Position**: top, center, bottom
    - **Styles**: bold, italic

    **Time formats:**
    - Seconds: "5 seconds", "10s"
    - Minutes: "1 minute 30 seconds", "1:30"
    - Full format: "0:01:30" (HH:MM:SS)

    Args:
        request: ChatRequest with session_id and message

    Returns:
        ChatResponse with AI response and updated subtitles

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/chat" \\
             -H "Content-Type: application/json" \\
             -d '{"session_id": "sess_abc123", "message": "Add subtitle Hello from 0 to 5 seconds"}'
        ```
    """
    # Validate session exists
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found or expired. Please upload a video first."
        )

    # Check if LLM is configured
    if settings.llm_provider == "openai" and not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file."
        )
    elif settings.llm_provider == "anthropic" and not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Anthropic API key not configured. Please set ANTHROPIC_API_KEY in .env file."
        )

    # Process message through LLM service
    try:
        result = await llm_service.process_message(
            session_id=request.session_id,
            user_message=request.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

    # Check for errors
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    # Convert subtitle dicts to Subtitle objects
    subtitles = [Subtitle(**sub) for sub in result["subtitles"]]

    # Create AI message
    ai_message = ChatMessage(
        type=MessageType.AI,
        content=result["ai_response"],
        metadata=result.get("extracted_params")
    )

    # Get video URL for preview (use Path for cross-platform compatibility)
    video_filename = Path(session.video_path).name
    video_url = f"/uploads/{video_filename}"

    return ChatResponse(
        session_id=request.session_id,
        message=ai_message,
        subtitles=subtitles,
        preview_url=video_url
    )


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get chat history for a session.

    Args:
        session_id: Session ID

    Returns:
        List of chat messages

    Example:
        ```bash
        curl "http://localhost:8000/api/chat/history/sess_abc123"
        ```
    """
    # Validate session
    if not session_manager.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    # Get chat history
    chat_history = session_manager.get_chat_history(session_id)

    return {
        "session_id": session_id,
        "messages": [msg.model_dump() for msg in chat_history],
        "count": len(chat_history)
    }


@router.get("/subtitles/{session_id}", response_model=List[Subtitle])
async def get_subtitles(session_id: str):
    """
    Get all subtitles for a session.

    Args:
        session_id: Session ID

    Returns:
        List of subtitles

    Example:
        ```bash
        curl "http://localhost:8000/api/subtitles/sess_abc123"
        ```
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    return session.subtitles


@router.delete("/subtitles/{session_id}")
async def clear_subtitles(session_id: str):
    """
    Clear all subtitles for a session.

    Args:
        session_id: Session ID

    Returns:
        Success message

    Example:
        ```bash
        curl -X DELETE "http://localhost:8000/api/subtitles/sess_abc123"
        ```
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    # Clear subtitles
    session_manager.update_subtitles(session_id, [])

    return {
        "message": f"All subtitles cleared for session {session_id}",
        "session_id": session_id
    }
