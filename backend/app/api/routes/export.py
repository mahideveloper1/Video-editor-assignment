"""
Export API endpoint for burning subtitles into video.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path
import uuid

from app.config import settings
from app.models.schemas import ExportRequest, ExportResponse
from app.services.video_service import video_service, VideoProcessingError
from app.services.subtitle_service import subtitle_service
from app.utils.session import session_manager
from app.utils.helpers import sanitize_filename


router = APIRouter()


@router.post("/export", response_model=ExportResponse)
async def export_video(request: ExportRequest):
    """
    Export video with burned-in subtitles.

    This endpoint:
    1. Generates an SRT/ASS subtitle file from current subtitles
    2. Burns the subtitles into the video using FFmpeg
    3. Returns a download URL for the final video

    **Note**: This process can take some time depending on video length and quality settings.

    Args:
        request: ExportRequest with session_id and optional filename

    Returns:
        ExportResponse with download URL

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/export" \\
             -H "Content-Type: application/json" \\
             -d '{"session_id": "sess_abc123", "filename": "my_video.mp4"}'
        ```
    """
    # Validate session
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found or expired"
        )

    # Check if there are subtitles to burn
    if not session.subtitles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No subtitles to export. Please add subtitles first using the chat endpoint."
        )

    # Get video path
    video_path = Path(session.video_path)
    if not video_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found"
        )

    # Generate output filename
    if request.filename:
        output_filename = sanitize_filename(request.filename)
    else:
        original_name = video_path.stem
        output_filename = f"{original_name}_subtitled.mp4"

    # Ensure .mp4 extension
    if not output_filename.endswith('.mp4'):
        output_filename += '.mp4'

    # Create unique output path
    unique_id = uuid.uuid4().hex[:8]
    final_output_filename = f"{unique_id}_{output_filename}"
    output_path = settings.output_dir / final_output_filename

    # Generate subtitle file (ASS format for better styling support)
    subtitle_filename = f"{unique_id}_subtitles.ass"
    subtitle_path = settings.temp_dir / subtitle_filename

    try:
        # Get video resolution for ASS subtitle generation
        width, height = video_service.get_resolution(video_path)

        # Generate ASS subtitle file
        subtitle_service.generate_ass(
            subtitles=session.subtitles,
            output_path=subtitle_path,
            video_width=width,
            video_height=height
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate subtitle file: {str(e)}"
        )

    # Burn subtitles into video
    try:
        video_service.burn_subtitles(
            video_path=video_path,
            subtitle_path=subtitle_path,
            output_path=output_path
        )
    except VideoProcessingError as e:
        # Clean up subtitle file
        subtitle_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to burn subtitles: {str(e)}"
        )

    # Clean up temporary subtitle file
    subtitle_path.unlink(missing_ok=True)

    # Generate download URL
    download_url = f"/outputs/{final_output_filename}"

    return ExportResponse(
        session_id=request.session_id,
        download_url=download_url,
        filename=output_filename,
        message="Video exported successfully with subtitles"
    )


@router.get("/download/{filename}")
async def download_video(filename: str):
    """
    Download an exported video file.

    Args:
        filename: Name of the file to download

    Returns:
        File download response

    Example:
        ```bash
        curl -O "http://localhost:8000/api/download/abc12345_video_subtitled.mp4"
        ```
    """
    # Sanitize filename
    safe_filename = sanitize_filename(filename)

    # Check output directory
    file_path = settings.output_dir / safe_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Return file for download
    return FileResponse(
        path=str(file_path),
        filename=safe_filename,
        media_type="video/mp4",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"'
        }
    )


@router.post("/preview/{session_id}")
async def generate_preview(session_id: str, duration: int = 10):
    """
    Generate a preview clip with subtitles (first N seconds).

    Args:
        session_id: Session ID
        duration: Preview duration in seconds (default: 10)

    Returns:
        Preview video URL

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/preview/sess_abc123?duration=15"
        ```
    """
    # Validate session
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    # Get video path
    video_path = Path(session.video_path)
    if not video_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found"
        )

    # Generate preview filename
    preview_filename = f"{session_id}_preview.mp4"
    preview_path = settings.temp_dir / preview_filename

    try:
        # Create preview clip
        video_service.create_preview_clip(
            video_path=video_path,
            output_path=preview_path,
            start_time=0.0,
            duration=float(duration)
        )
    except VideoProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
        )

    return {
        "session_id": session_id,
        "preview_url": f"/temp/{preview_filename}",
        "duration": duration,
        "message": "Preview generated successfully"
    }


@router.get("/export/status/{session_id}")
async def get_export_status(session_id: str):
    """
    Get export status and available exports for a session.

    Args:
        session_id: Session ID

    Returns:
        Export status information

    Example:
        ```bash
        curl "http://localhost:8000/api/export/status/sess_abc123"
        ```
    """
    # Validate session
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    # Check for existing exports
    output_files = list(settings.output_dir.glob(f"*{session_id}*"))

    exports = [
        {
            "filename": f.name,
            "size": f.stat().st_size,
            "download_url": f"/outputs/{f.name}"
        }
        for f in output_files
    ]

    return {
        "session_id": session_id,
        "subtitle_count": len(session.subtitles),
        "can_export": len(session.subtitles) > 0,
        "exports": exports,
        "message": "Ready to export" if session.subtitles else "Add subtitles first"
    }
