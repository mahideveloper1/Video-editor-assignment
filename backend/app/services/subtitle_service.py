"""
Subtitle service for SRT generation and subtitle management.
Handles conversion of subtitle objects to SRT format and styling.
"""

from pathlib import Path
from typing import List, Optional
import re

from app.models.schemas import Subtitle, SubtitleStyle, SubtitlePosition
from app.utils.helpers import format_time, color_name_to_hex, hex_to_rgb
from app.config import settings


class SubtitleService:
    """Service for subtitle generation and SRT file creation."""

    def generate_srt(
        self,
        subtitles: List[Subtitle],
        output_path: Path
    ) -> Path:
        """
        Generate SRT subtitle file from subtitle objects.

        Args:
            subtitles: List of Subtitle objects
            output_path: Path for output SRT file

        Returns:
            Path to generated SRT file
        """
        # Sort subtitles by start time
        sorted_subtitles = sorted(subtitles, key=lambda s: s.start_time)

        srt_content = []

        for idx, subtitle in enumerate(sorted_subtitles, start=1):
            # Subtitle index
            srt_content.append(str(idx))

            # Timestamp line (HH:MM:SS,mmm --> HH:MM:SS,mmm)
            start_time = format_time(subtitle.start_time)
            end_time = format_time(subtitle.end_time)
            srt_content.append(f"{start_time} --> {end_time}")

            # Subtitle text (with optional styling)
            styled_text = self._apply_text_styling(subtitle.text, subtitle.style)
            srt_content.append(styled_text)

            # Blank line between entries
            srt_content.append("")

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(srt_content), encoding="utf-8")

        return output_path

    def generate_ass(
        self,
        subtitles: List[Subtitle],
        output_path: Path,
        video_width: int = 1920,
        video_height: int = 1080
    ) -> Path:
        """
        Generate ASS (Advanced SubStation Alpha) subtitle file with full styling support.
        ASS format supports more advanced styling than SRT.

        Args:
            subtitles: List of Subtitle objects
            output_path: Path for output ASS file
            video_width: Video width for positioning
            video_height: Video height for positioning

        Returns:
            Path to generated ASS file
        """
        # Sort subtitles by start time
        sorted_subtitles = sorted(subtitles, key=lambda s: s.start_time)

        # ASS file header
        ass_content = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: {}".format(video_width),
            "PlayResY: {}".format(video_height),
            "WrapStyle: 0",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        ]

        # Create styles for each unique style configuration
        unique_styles = self._get_unique_styles(sorted_subtitles)
        for style_name, style in unique_styles.items():
            ass_content.append(self._create_ass_style(style_name, style, video_height))

        # Events section
        ass_content.extend([
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        ])

        # Add dialogue events
        for subtitle in sorted_subtitles:
            style_name = self._get_style_name(subtitle.style)
            start_time = self._format_ass_time(subtitle.start_time)
            end_time = self._format_ass_time(subtitle.end_time)

            # Clean text (remove SRT formatting tags)
            text = subtitle.text.replace("\n", "\\N")

            dialogue = f"Dialogue: 0,{start_time},{end_time},{style_name},,0,0,0,,{text}"
            ass_content.append(dialogue)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(ass_content), encoding="utf-8")

        return output_path

    def _apply_text_styling(self, text: str, style: SubtitleStyle) -> str:
        """
        Apply basic HTML-like styling to subtitle text for SRT.

        Note: SRT has limited styling support. For advanced styling,
        use ASS format or burn subtitles with FFmpeg filters.

        Args:
            text: Original subtitle text
            style: SubtitleStyle object

        Returns:
            Styled text string
        """
        styled_text = text

        # Apply bold
        if style.bold:
            styled_text = f"<b>{styled_text}</b>"

        # Apply italic
        if style.italic:
            styled_text = f"<i>{styled_text}</i>"

        # Note: SRT doesn't support font color/family in standard format
        # These would need to be applied via ASS format or FFmpeg filters

        return styled_text

    def _get_unique_styles(self, subtitles: List[Subtitle]) -> dict:
        """
        Extract unique styles from subtitle list.

        Args:
            subtitles: List of subtitles

        Returns:
            Dictionary of style_name -> SubtitleStyle
        """
        unique_styles = {}

        for subtitle in subtitles:
            style_name = self._get_style_name(subtitle.style)
            if style_name not in unique_styles:
                unique_styles[style_name] = subtitle.style

        # Always include default style
        if "Default" not in unique_styles:
            unique_styles["Default"] = SubtitleStyle()

        return unique_styles

    def _get_style_name(self, style: SubtitleStyle) -> str:
        """
        Generate a unique style name from SubtitleStyle.

        Args:
            style: SubtitleStyle object

        Returns:
            Style name string
        """
        # Create a simple hash-like name based on style properties
        name_parts = [
            style.font_family.replace(" ", ""),
            str(style.font_size),
            style.font_color.replace("#", "")[:6],
        ]
        return "_".join(name_parts)

    def _create_ass_style(
        self,
        style_name: str,
        style: SubtitleStyle,
        video_height: int
    ) -> str:
        """
        Create ASS style definition.

        Args:
            style_name: Name for the style
            style: SubtitleStyle object
            video_height: Video height for positioning

        Returns:
            ASS style definition string
        """
        # Convert color to ASS format (&HAABBGGRR)
        primary_color = self._color_to_ass(style.font_color)

        # Background color (if specified)
        back_color = self._color_to_ass(style.background_color) if style.background_color else "&H00000000"

        # Outline and shadow
        outline_color = "&H00000000"  # Black outline
        shadow_color = "&H80000000"   # Semi-transparent black shadow

        # Bold and italic
        bold = "-1" if style.bold else "0"
        italic = "-1" if style.italic else "0"

        # Alignment (ASS uses numpad positions)
        # 1=bottom-left, 2=bottom-center, 3=bottom-right
        # 4=middle-left, 5=middle-center, 6=middle-right
        # 7=top-left, 8=top-center, 9=top-right
        alignment_map = {
            SubtitlePosition.BOTTOM: "2",
            SubtitlePosition.CENTER: "5",
            SubtitlePosition.TOP: "8"
        }
        alignment = alignment_map.get(style.position, "2")

        # Margin from bottom
        margin_v = "20"  # pixels from edge

        # Style format:
        # Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour,
        # Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle,
        # BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding

        return (
            f"Style: {style_name},{style.font_family},{style.font_size},"
            f"{primary_color},{primary_color},{outline_color},{back_color},"
            f"{bold},{italic},0,0,100,100,0,0,1,2,1,{alignment},10,10,{margin_v},1"
        )

    def _color_to_ass(self, color: str) -> str:
        """
        Convert color name or hex to ASS color format (&HAABBGGRR).

        Args:
            color: Color name or hex string

        Returns:
            ASS color format string
        """
        # Convert color name to hex if needed
        if not color.startswith("#"):
            color = color_name_to_hex(color)

        # Convert hex to RGB
        rgb = hex_to_rgb(color)
        if not rgb:
            rgb = (255, 255, 255)  # Default to white

        r, g, b = rgb

        # ASS format is &HAABBGGRR (reversed RGB with alpha)
        return f"&H00{b:02X}{g:02X}{r:02X}"

    def _format_ass_time(self, seconds: float) -> str:
        """
        Format seconds to ASS time format (H:MM:SS.xx).

        Args:
            seconds: Time in seconds

        Returns:
            ASS formatted time string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centiseconds = int((seconds % 1) * 100)

        return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"

    def validate_subtitle_times(self, subtitles: List[Subtitle]) -> List[str]:
        """
        Validate subtitle timing (no overlaps, valid ranges).

        Args:
            subtitles: List of subtitles to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Sort by start time
        sorted_subs = sorted(subtitles, key=lambda s: s.start_time)

        for i, sub in enumerate(sorted_subs):
            # Check if end time is after start time
            if sub.end_time <= sub.start_time:
                errors.append(
                    f"Subtitle {sub.id}: End time ({sub.end_time}) must be after start time ({sub.start_time})"
                )

            # Check for negative times
            if sub.start_time < 0 or sub.end_time < 0:
                errors.append(
                    f"Subtitle {sub.id}: Times cannot be negative"
                )

            # Check for overlaps with next subtitle
            if i < len(sorted_subs) - 1:
                next_sub = sorted_subs[i + 1]
                if sub.end_time > next_sub.start_time:
                    errors.append(
                        f"Subtitle {sub.id} overlaps with {next_sub.id}"
                    )

        return errors

    def merge_subtitles(
        self,
        existing: List[Subtitle],
        new: List[Subtitle]
    ) -> List[Subtitle]:
        """
        Merge new subtitles with existing ones, avoiding duplicates.

        Args:
            existing: Existing subtitle list
            new: New subtitles to add

        Returns:
            Merged subtitle list
        """
        # Create a dictionary for quick lookup by ID
        merged = {sub.id: sub for sub in existing}

        # Add or update with new subtitles
        for sub in new:
            merged[sub.id] = sub

        # Return as sorted list
        return sorted(merged.values(), key=lambda s: s.start_time)

    def create_default_style(self) -> SubtitleStyle:
        """
        Create default subtitle style from settings.

        Returns:
            SubtitleStyle with default values
        """
        return SubtitleStyle(
            font_family=settings.default_font_family,
            font_size=settings.default_font_size,
            font_color=settings.default_font_color,
            position=SubtitlePosition(settings.default_subtitle_position),
            bold=False,
            italic=False
        )


# Global subtitle service instance
subtitle_service = SubtitleService()
