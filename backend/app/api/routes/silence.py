"""
Silence Detection and Removal Routes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import logging
from typing import Optional, List
from pathlib import Path

from app.services.silence_remover_service import SilenceRemoverService
from app.utils.session import session_manager
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["silence"])


class RemoveSilenceRequest(BaseModel):
    """Request model for removing silence"""
    session_id: str
    noise_threshold: Optional[str] = "-30dB"
    min_silence_duration: Optional[float] = 1.0


class RemoveSilenceResponse(BaseModel):
    """Response model for silence removal"""
    session_id: str
    message: str
    silence_removed: bool
    stats: dict
    preview_url: str
    subtitles: Optional[List] = []


def adjust_subtitle_timestamps(subtitles, silence_segments):
    """
    Adjust subtitle timestamps after silence removal

    Args:
        subtitles: List of Subtitle objects
        silence_segments: List of SilenceSegment objects that were removed

    Returns:
        List of Subtitle objects with adjusted timestamps
    """
    if not subtitles or not silence_segments:
        return subtitles

    adjusted_subtitles = []

    for subtitle in subtitles:
        # Calculate how much silence was removed before start_time
        time_removed_before_start = sum(
            seg.duration for seg in silence_segments
            if seg.end <= subtitle.start_time
        )

        # Calculate how much silence was removed before end_time
        time_removed_before_end = sum(
            seg.duration for seg in silence_segments
            if seg.end <= subtitle.end_time
        )

        # Adjust timestamps
        new_start = subtitle.start_time - time_removed_before_start
        new_end = subtitle.end_time - time_removed_before_end

        # Only include subtitle if it's still valid (not within removed silence)
        if new_start >= 0 and new_end > new_start:
            subtitle.start_time = round(new_start, 2)
            subtitle.end_time = round(new_end, 2)
            adjusted_subtitles.append(subtitle)

    return adjusted_subtitles


@router.post("/remove-silence", response_model=RemoveSilenceResponse)
async def remove_silence(request: RemoveSilenceRequest):
    """
    Remove silent segments from uploaded video

    Args:
        request: RemoveSilenceRequest with session_id and optional parameters

    Returns:
        RemoveSilenceResponse with processed video info
    """
    try:
        # Get session
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get video path
        video_path = session.video_path
        if not video_path or not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video not found")

        # Initialize silence remover service
        service = SilenceRemoverService(
            noise_threshold=request.noise_threshold,
            min_silence_duration=request.min_silence_duration
        )

        # Detect silence
        logger.info(f"Detecting silence in video for session {request.session_id}")
        silence_segments, total_duration = service.detect_silence(video_path)

        if not silence_segments:
            return RemoveSilenceResponse(
                session_id=request.session_id,
                message="No silence detected in video",
                silence_removed=False,
                stats={"total_silence_duration": 0, "silence_percentage": 0, "num_silent_segments": 0},
                preview_url=f"/uploads/{os.path.basename(video_path)}",
                subtitles=[sub.dict() for sub in session.subtitles] if session.subtitles else []
            )

        # Get stats
        stats = service.get_silence_stats(silence_segments, total_duration)

        # Create output path
        filename = os.path.basename(video_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_no_silence{ext}"
        output_path = str(settings.upload_dir / output_filename)

        # Remove silence
        logger.info(f"Removing {len(silence_segments)} silent segments from video")
        service.remove_silence(video_path, output_path, silence_segments)

        # Adjust subtitle timestamps
        if session.subtitles:
            logger.info(f"Adjusting {len(session.subtitles)} subtitle timestamps")
            adjusted_subtitles = adjust_subtitle_timestamps(session.subtitles, silence_segments)
            session.subtitles = adjusted_subtitles
            logger.info(f"Adjusted subtitles: {len(adjusted_subtitles)} remaining")

        # Update session with new video path
        session.video_path = output_path

        logger.info(f"Successfully removed silence for session {request.session_id}")

        return RemoveSilenceResponse(
            session_id=request.session_id,
            message=f"Removed {stats['num_silent_segments']} silent segments ({stats['total_silence_duration']}s)",
            silence_removed=True,
            stats=stats,
            preview_url=f"/uploads/{output_filename}",
            subtitles=[sub.dict() for sub in session.subtitles] if session.subtitles else []
        )

    except Exception as e:
        logger.error(f"Error removing silence: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to remove silence: {str(e)}")


@router.post("/detect-silence")
async def detect_silence(request: RemoveSilenceRequest):
    """
    Detect silent segments without removing them

    Args:
        request: RemoveSilenceRequest with session_id and optional parameters

    Returns:
        Silence detection results
    """
    try:
        # Get session
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get video path
        video_path = session.video_path
        if not video_path or not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video not found")

        # Initialize silence remover service
        service = SilenceRemoverService(
            noise_threshold=request.noise_threshold,
            min_silence_duration=request.min_silence_duration
        )

        # Detect silence
        logger.info(f"Detecting silence in video for session {request.session_id}")
        silence_segments, total_duration = service.detect_silence(video_path)

        # Get stats
        stats = service.get_silence_stats(silence_segments, total_duration)

        # Note: Storing in session would require extending the VideoSession model
        # For now, just return the results

        return {
            "session_id": request.session_id,
            "silence_segments": [s.to_dict() for s in silence_segments],
            "stats": stats
        }

    except Exception as e:
        logger.error(f"Error detecting silence: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to detect silence: {str(e)}")
