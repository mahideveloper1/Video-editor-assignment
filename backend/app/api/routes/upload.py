"""
Video upload API endpoint.
Handles video file uploads and session creation.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pathlib import Path
import aiofiles
import uuid

from app.config import settings
from app.models.schemas import UploadResponse, ErrorResponse
from app.services.video_service import video_service, VideoProcessingError
from app.services.silence_remover_service import SilenceRemoverService
from app.utils.session import session_manager
from app.utils.helpers import sanitize_filename
import logging

logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    file: UploadFile = File(..., description="Video file to upload")
):
    """
    Upload a video file and create a new editing session.

    - Accepts: MP4, MOV, AVI, WebM formats
    - Max size: 500MB
    - Returns: Session ID and video metadata

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/upload" \\
             -F "file=@video.mp4"
        ```
    """
    # Validate file was provided
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_video_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format. Allowed formats: {', '.join(settings.allowed_video_formats)}"
        )

    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)

    # Generate unique filename to avoid conflicts
    unique_id = uuid.uuid4().hex[:8]
    final_filename = f"{unique_id}_{safe_filename}"
    video_path = settings.upload_dir / final_filename

    try:
        # Save uploaded file
        async with aiofiles.open(video_path, 'wb') as out_file:
            # Read and write in chunks to handle large files
            chunk_size = 1024 * 1024  # 1MB chunks
            total_size = 0

            while content := await file.read(chunk_size):
                total_size += len(content)

                # Check file size limit
                if total_size > settings.max_upload_size:
                    # Remove partial file
                    video_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File too large. Maximum size: {settings.max_upload_size / (1024*1024):.0f}MB"
                    )

                await out_file.write(content)

    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        video_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Extract video metadata
    try:
        metadata = video_service.extract_metadata(video_path)
    except VideoProcessingError as e:
        # Clean up invalid video file
        video_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid video file: {str(e)}"
        )

    # Detect silence in video
    silence_data = None
    try:
        logger.info(f"Detecting silence in uploaded video: {final_filename}")
        silence_service = SilenceRemoverService(
            noise_threshold="-30dB",
            min_silence_duration=1.0
        )
        silence_segments, total_duration = silence_service.detect_silence(str(video_path))

        if silence_segments:
            silence_stats = silence_service.get_silence_stats(silence_segments, total_duration)
            silence_data = {
                "has_silence": True,
                "segments": [s.to_dict() for s in silence_segments],
                "stats": silence_stats
            }
            logger.info(f"Detected {len(silence_segments)} silent segments ({silence_stats['total_silence_duration']}s)")
        else:
            silence_data = {
                "has_silence": False,
                "segments": [],
                "stats": {"total_silence_duration": 0, "silence_percentage": 0, "num_silent_segments": 0}
            }
            logger.info("No silence detected in video")
    except Exception as e:
        logger.warning(f"Failed to detect silence (non-critical): {str(e)}")
        # Don't fail the upload if silence detection fails
        silence_data = None

    # Create editing session
    try:
        session = session_manager.create_session(
            video_path=str(video_path),
            metadata=metadata
        )
        # Note: silence_data is returned in the response, not stored in session

    except Exception as e:
        # Clean up on error
        video_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )

    # Build response
    response_data = {
        "session_id": session.session_id,
        "filename": safe_filename,
        "metadata": metadata,
        "message": "Video uploaded successfully"
    }

    # Add silence data to response if available
    if silence_data:
        response_data["silence_detection"] = silence_data

    return UploadResponse(**response_data)


@router.get("/video/{session_id}")
async def get_video_info(session_id: str):
    """
    Get video information for a session.

    Args:
        session_id: Session ID

    Returns:
        Video metadata and session info
    """
    session = session_manager.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found or expired"
        )

    return {
        "session_id": session.session_id,
        "metadata": session.metadata,
        "video_url": f"/uploads/{Path(session.video_path).name}",
        "subtitle_count": len(session.subtitles),
        "created_at": session.created_at
    }


@router.delete("/video/{session_id}")
async def delete_video_session(session_id: str):
    """
    Delete a video editing session and cleanup files.

    Args:
        session_id: Session ID

    Returns:
        Success message
    """
    if not session_manager.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    success = session_manager.delete_session(session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )

    return {
        "message": f"Session {session_id} deleted successfully"
    }
