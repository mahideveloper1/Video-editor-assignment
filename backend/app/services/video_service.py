"""
Video processing service using FFmpeg.
Handles video metadata extraction, validation, and processing.
"""

import ffmpeg
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from app.config import settings
from app.models.schemas import VideoMetadata
from app.utils.helpers import validate_video_file


class VideoProcessingError(Exception):
    """Custom exception for video processing errors."""
    pass


class VideoService:
    """Service for video processing operations using FFmpeg."""

    def __init__(self):
        self._verify_ffmpeg_installation()

    def _verify_ffmpeg_installation(self):
        """Verify FFmpeg is installed and accessible."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise VideoProcessingError(
                "FFmpeg is not installed or not accessible. "
                "Please install FFmpeg: https://ffmpeg.org/download.html"
            )

    def extract_metadata(self, video_path: Path) -> VideoMetadata:
        """
        Extract video metadata using FFmpeg probe.

        Args:
            video_path: Path to video file

        Returns:
            VideoMetadata object

        Raises:
            VideoProcessingError: If metadata extraction fails
        """
        # Validate file first
        is_valid, error_msg = validate_video_file(video_path)
        if not is_valid:
            raise VideoProcessingError(f"Invalid video file: {error_msg}")

        try:
            # Use ffprobe to get video information
            probe = ffmpeg.probe(str(video_path))

            # Find video stream
            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
                None
            )

            if not video_stream:
                raise VideoProcessingError("No video stream found in file")

            # Extract metadata
            duration = float(probe['format'].get('duration', 0))
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))

            # Calculate FPS
            fps_str = video_stream.get('r_frame_rate', '0/1')
            fps_parts = fps_str.split('/')
            fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else 0.0

            # Get format
            video_format = probe['format'].get('format_name', 'unknown')
            codec = video_stream.get('codec_name', 'unknown')

            # Get file size
            file_size = video_path.stat().st_size

            return VideoMetadata(
                filename=video_path.name,
                duration=duration,
                width=width,
                height=height,
                fps=fps,
                format=f"{video_format} ({codec})",
                size=file_size
            )

        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise VideoProcessingError(f"FFmpeg error: {error_message}")
        except Exception as e:
            raise VideoProcessingError(f"Failed to extract metadata: {str(e)}")

    def get_video_info(self, video_path: Path) -> Dict[str, Any]:
        """
        Get detailed video information using ffprobe.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with detailed video information
        """
        try:
            probe = ffmpeg.probe(str(video_path))
            return probe
        except ffmpeg.Error as e:
            raise VideoProcessingError(f"Failed to get video info: {str(e)}")

    def validate_video(self, video_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate video file can be processed.

        Args:
            video_path: Path to video file

        Returns:
            Tuple of (is_valid, error_message)
        """
        # First check file validity
        is_valid, error_msg = validate_video_file(video_path)
        if not is_valid:
            return False, error_msg

        # Try to extract metadata to ensure file is readable
        try:
            self.extract_metadata(video_path)
            return True, None
        except VideoProcessingError as e:
            return False, str(e)

    def get_video_duration(self, video_path: Path) -> float:
        """
        Get video duration in seconds.

        Args:
            video_path: Path to video file

        Returns:
            Duration in seconds
        """
        try:
            probe = ffmpeg.probe(str(video_path))
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            raise VideoProcessingError(f"Failed to get duration: {str(e)}")

    def generate_thumbnail(
        self,
        video_path: Path,
        output_path: Path,
        timestamp: float = 1.0
    ) -> Path:
        """
        Generate a thumbnail from video at specific timestamp.

        Args:
            video_path: Path to video file
            output_path: Path for output thumbnail
            timestamp: Time in seconds to capture thumbnail

        Returns:
            Path to generated thumbnail
        """
        try:
            (
                ffmpeg
                .input(str(video_path), ss=timestamp)
                .output(str(output_path), vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_path
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise VideoProcessingError(f"Failed to generate thumbnail: {error_message}")

    def create_preview_clip(
        self,
        video_path: Path,
        output_path: Path,
        start_time: float = 0.0,
        duration: float = 10.0
    ) -> Path:
        """
        Create a short preview clip from video.

        Args:
            video_path: Path to video file
            output_path: Path for output preview
            start_time: Start time in seconds
            duration: Duration of preview in seconds

        Returns:
            Path to generated preview
        """
        try:
            (
                ffmpeg
                .input(str(video_path), ss=start_time, t=duration)
                .output(
                    str(output_path),
                    vcodec='libx264',
                    acodec='aac',
                    **{'crf': '23', 'preset': 'fast'}
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_path
        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise VideoProcessingError(f"Failed to create preview: {error_message}")

    def burn_subtitles(
        self,
        video_path: Path,
        subtitle_path: Path,
        output_path: Path
    ) -> Path:
        """
        Burn subtitles into video file.

        Args:
            video_path: Path to input video
            subtitle_path: Path to SRT subtitle file
            output_path: Path for output video

        Returns:
            Path to output video with burned subtitles

        Raises:
            VideoProcessingError: If subtitle burning fails
        """
        try:
            # Get video quality settings
            quality_settings = self._get_quality_settings()

            # Build FFmpeg command to burn subtitles
            (
                ffmpeg
                .input(str(video_path))
                .output(
                    str(output_path),
                    vf=f"subtitles={subtitle_path}",
                    **quality_settings
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            return output_path

        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            raise VideoProcessingError(f"Failed to burn subtitles: {error_message}")

    def _get_quality_settings(self) -> Dict[str, Any]:
        """
        Get FFmpeg quality settings based on configuration.

        Returns:
            Dictionary of FFmpeg output parameters
        """
        quality = settings.video_quality.lower()

        settings_map = {
            'high': {
                'vcodec': 'libx264',
                'acodec': 'aac',
                'crf': '18',
                'preset': 'slow',
                'threads': str(settings.ffmpeg_threads)
            },
            'medium': {
                'vcodec': 'libx264',
                'acodec': 'aac',
                'crf': '23',
                'preset': 'medium',
                'threads': str(settings.ffmpeg_threads)
            },
            'low': {
                'vcodec': 'libx264',
                'acodec': 'aac',
                'crf': '28',
                'preset': 'fast',
                'threads': str(settings.ffmpeg_threads)
            }
        }

        return settings_map.get(quality, settings_map['medium'])

    def get_resolution(self, video_path: Path) -> Tuple[int, int]:
        """
        Get video resolution (width, height).

        Args:
            video_path: Path to video file

        Returns:
            Tuple of (width, height)
        """
        try:
            probe = ffmpeg.probe(str(video_path))
            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
                None
            )
            if video_stream:
                return int(video_stream['width']), int(video_stream['height'])
            else:
                raise VideoProcessingError("No video stream found")
        except Exception as e:
            raise VideoProcessingError(f"Failed to get resolution: {str(e)}")


# Global video service instance
video_service = VideoService()
