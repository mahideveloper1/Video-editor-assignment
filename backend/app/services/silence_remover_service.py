"""
Silence Detection and Removal Service

Detects silent segments in videos and removes them using FFmpeg.
"""

import os
import re
import subprocess
import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class SilenceSegment:
    """Represents a silent segment in a video"""
    def __init__(self, start: float, end: float, duration: float):
        self.start = start
        self.end = end
        self.duration = duration

    def to_dict(self) -> Dict:
        return {
            "start": round(self.start, 2),
            "end": round(self.end, 2),
            "duration": round(self.duration, 2)
        }


class SilenceRemoverService:
    """Service for detecting and removing silence from videos"""

    def __init__(
        self,
        noise_threshold: str = "-30dB",
        min_silence_duration: float = 1.0
    ):
        """
        Initialize silence remover service

        Args:
            noise_threshold: Volume threshold for silence (e.g., "-30dB")
            min_silence_duration: Minimum duration of silence to detect (seconds)
        """
        self.noise_threshold = noise_threshold
        self.min_silence_duration = min_silence_duration

    def detect_silence(self, video_path: str) -> Tuple[List[SilenceSegment], float]:
        """
        Detect silent segments in a video

        Args:
            video_path: Path to the video file

        Returns:
            Tuple of (list of silence segments, total video duration)
        """
        try:
            # Run FFmpeg silence detection
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-af", f"silencedetect=noise={self.noise_threshold}:d={self.min_silence_duration}",
                "-f", "null",
                "-"
            ]

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output = result.stderr

            # Parse silence segments from FFmpeg output
            silence_segments = self._parse_silence_output(output)

            # Get video duration
            duration = self._get_video_duration(video_path)

            logger.info(f"Detected {len(silence_segments)} silent segments in {video_path}")

            return silence_segments, duration

        except Exception as e:
            logger.error(f"Error detecting silence: {str(e)}")
            raise

    def _parse_silence_output(self, output: str) -> List[SilenceSegment]:
        """
        Parse FFmpeg silence detection output

        Args:
            output: FFmpeg stderr output

        Returns:
            List of SilenceSegment objects
        """
        segments = []

        # Pattern to match silence_start and silence_end
        start_pattern = r"silence_start: ([\d.]+)"
        end_pattern = r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)"

        starts = re.finditer(start_pattern, output)
        ends = re.finditer(end_pattern, output)

        start_times = [float(m.group(1)) for m in starts]
        end_data = [(float(m.group(1)), float(m.group(2))) for m in ends]

        # Match starts with ends
        for i, (end_time, duration) in enumerate(end_data):
            if i < len(start_times):
                start_time = start_times[i]
                segments.append(SilenceSegment(start_time, end_time, duration))

        return segments

    def _get_video_duration(self, video_path: str) -> float:
        """
        Get total video duration using FFprobe

        Args:
            video_path: Path to the video file

        Returns:
            Duration in seconds
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        duration = float(result.stdout.strip())

        return duration

    def remove_silence(
        self,
        input_path: str,
        output_path: str,
        silence_segments: Optional[List[SilenceSegment]] = None
    ) -> str:
        """
        Remove silent segments from video

        Args:
            input_path: Path to input video
            output_path: Path to output video
            silence_segments: Optional list of silence segments (will detect if not provided)

        Returns:
            Path to output video
        """
        try:
            # Detect silence if not provided
            if silence_segments is None:
                silence_segments, _ = self.detect_silence(input_path)

            if not silence_segments:
                logger.info("No silence detected, copying original video")
                # No silence to remove, just copy the file
                subprocess.run(["cp", input_path, output_path], check=True)
                return output_path

            # Get video duration
            duration = self._get_video_duration(input_path)

            # Calculate non-silent segments (parts to keep)
            keep_segments = self._calculate_keep_segments(silence_segments, duration)

            if not keep_segments:
                raise ValueError("No non-silent segments found in video")

            # Create filter complex for cutting and concatenating
            filter_complex = self._build_filter_complex(keep_segments)

            # Run FFmpeg to remove silence
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-filter_complex", filter_complex,
                "-map", "[outv]",
                "-map", "[outa]",
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                "-b:a", "192k",
                "-y",
                output_path
            ]

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg error: {result.stderr}")

            logger.info(f"Successfully removed silence from {input_path} -> {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"Error removing silence: {str(e)}")
            raise

    def _calculate_keep_segments(
        self,
        silence_segments: List[SilenceSegment],
        total_duration: float
    ) -> List[Tuple[float, float]]:
        """
        Calculate non-silent segments to keep

        Args:
            silence_segments: List of silent segments
            total_duration: Total video duration

        Returns:
            List of (start, end) tuples for segments to keep
        """
        keep_segments = []
        current_time = 0.0

        for silence in silence_segments:
            # Add segment before this silence
            if silence.start > current_time:
                keep_segments.append((current_time, silence.start))
            current_time = silence.end

        # Add final segment after last silence
        if current_time < total_duration:
            keep_segments.append((current_time, total_duration))

        return keep_segments

    def _build_filter_complex(self, keep_segments: List[Tuple[float, float]]) -> str:
        """
        Build FFmpeg filter_complex for cutting and concatenating segments

        Args:
            keep_segments: List of (start, end) tuples

        Returns:
            FFmpeg filter_complex string
        """
        if len(keep_segments) == 1:
            # Single segment - just trim
            start, end = keep_segments[0]
            return (
                f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[outv];"
                f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[outa]"
            )

        # Multiple segments - need to concatenate
        filter_parts = []

        # Create trim filters for each segment
        for i, (start, end) in enumerate(keep_segments):
            filter_parts.append(
                f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}];"
                f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}]"
            )

        # Concatenate all segments
        video_inputs = "".join([f"[v{i}]" for i in range(len(keep_segments))])
        audio_inputs = "".join([f"[a{i}]" for i in range(len(keep_segments))])

        concat_filter = (
            f"{video_inputs}concat=n={len(keep_segments)}:v=1:a=0[outv];"
            f"{audio_inputs}concat=n={len(keep_segments)}:v=0:a=1[outa]"
        )

        return ";".join(filter_parts) + ";" + concat_filter

    def get_silence_stats(
        self,
        silence_segments: List[SilenceSegment],
        total_duration: float
    ) -> Dict:
        """
        Get statistics about silence in video

        Args:
            silence_segments: List of silent segments
            total_duration: Total video duration

        Returns:
            Dictionary with silence statistics
        """
        total_silence = sum(s.duration for s in silence_segments)
        silence_percentage = (total_silence / total_duration * 100) if total_duration > 0 else 0

        return {
            "total_silence_duration": round(total_silence, 2),
            "silence_percentage": round(silence_percentage, 2),
            "num_silent_segments": len(silence_segments),
            "total_duration": round(total_duration, 2),
            "duration_after_removal": round(total_duration - total_silence, 2)
        }
