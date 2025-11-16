"""
Utility helper functions for the backend.
"""

import uuid
import re
from pathlib import Path
from typing import Optional, Tuple


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique_id = uuid.uuid4().hex[:12]
    return f"{prefix}_{unique_id}" if prefix else unique_id


def format_time(seconds: float) -> str:
    """
    Format seconds to SRT time format (HH:MM:SS,mmm).

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def parse_time_string(time_str: str) -> Optional[float]:
    """
    Parse natural language time string to seconds.

    Examples:
        "5 seconds" -> 5.0
        "1 minute 30 seconds" -> 90.0
        "1:30" -> 90.0
        "00:01:30" -> 90.0

    Args:
        time_str: Time string

    Returns:
        Time in seconds or None if parse fails
    """
    time_str = time_str.lower().strip()

    # Try HH:MM:SS or MM:SS format
    time_parts = time_str.split(":")
    if len(time_parts) in [2, 3]:
        try:
            if len(time_parts) == 2:  # MM:SS
                minutes, seconds = map(float, time_parts)
                return minutes * 60 + seconds
            else:  # HH:MM:SS
                hours, minutes, seconds = map(float, time_parts)
                return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            pass

    # Try natural language parsing
    total_seconds = 0.0

    # Extract hours
    hours_match = re.search(r'(\d+)\s*(?:hour|hr|h)', time_str)
    if hours_match:
        total_seconds += float(hours_match.group(1)) * 3600

    # Extract minutes
    minutes_match = re.search(r'(\d+)\s*(?:minute|min|m)', time_str)
    if minutes_match:
        total_seconds += float(minutes_match.group(1)) * 60

    # Extract seconds
    seconds_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:second|sec|s)', time_str)
    if seconds_match:
        total_seconds += float(seconds_match.group(1))

    # If just a number, assume seconds
    if total_seconds == 0:
        try:
            total_seconds = float(time_str)
        except ValueError:
            return None

    return total_seconds if total_seconds > 0 else None


def validate_video_file(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate video file exists and has correct format.

    Args:
        file_path: Path to video file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path.exists():
        return False, "File does not exist"

    if not file_path.is_file():
        return False, "Path is not a file"

    # Check file extension
    allowed_extensions = ['.mp4', '.mov', '.avi', '.webm']
    if file_path.suffix.lower() not in allowed_extensions:
        return False, f"Invalid file format. Allowed: {', '.join(allowed_extensions)}"

    # Check file size
    file_size = file_path.stat().st_size
    max_size = 500 * 1024 * 1024  # 500MB
    if file_size > max_size:
        return False, f"File too large. Max size: {max_size / (1024*1024):.0f}MB"

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove dangerous characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = Path(filename).name

    # Replace spaces and special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'\s+', '_', filename)

    return filename


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def hex_to_rgb(hex_color: str) -> Optional[Tuple[int, int, int]]:
    """
    Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#FF0000" or "FF0000")

    Returns:
        RGB tuple or None if invalid
    """
    hex_color = hex_color.lstrip('#')

    if len(hex_color) != 6:
        return None

    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def color_name_to_hex(color_name: str) -> str:
    """
    Convert color name to hex value.

    Args:
        color_name: Color name (e.g., "red", "blue")

    Returns:
        Hex color string
    """
    color_map = {
        'white': '#FFFFFF',
        'black': '#000000',
        'red': '#FF0000',
        'green': '#00FF00',
        'blue': '#0000FF',
        'yellow': '#FFFF00',
        'cyan': '#00FFFF',
        'magenta': '#FF00FF',
        'orange': '#FFA500',
        'purple': '#800080',
        'pink': '#FFC0CB',
        'brown': '#A52A2A',
        'gray': '#808080',
        'grey': '#808080',
    }

    return color_map.get(color_name.lower(), '#FFFFFF')
