"""
LangGraph state definitions for the video editing workflow.
"""

from typing import TypedDict, List, Optional, Dict, Any, Annotated
from operator import add


class SubtitleEdit(TypedDict, total=False):
    """Represents a single subtitle to be added/edited."""
    subtitle_index: Optional[int]  # Index of subtitle to modify (-1 for last, None for new)
    text: str
    start_time: float
    end_time: float
    font_family: Optional[str]
    font_size: Optional[int]
    font_color: Optional[str]
    position: Optional[str]
    bold: Optional[bool]
    italic: Optional[bool]


class VideoEditState(TypedDict, total=False):
    """
    State for the video editing LangGraph workflow.
    This state is passed through all nodes in the graph.
    """
    # Session information
    session_id: str

    # User input
    user_message: str

    # Parsed intent and parameters
    intent: Optional[str]  # "add_subtitle", "modify_subtitle", "remove_subtitle", etc.
    extracted_params: Optional[Dict[str, Any]]

    # Current subtitles (list of subtitle dicts)
    current_subtitles: Annotated[List[Dict[str, Any]], add]

    # Subtitle edits to apply
    subtitle_edits: Optional[List[SubtitleEdit]]

    # Track modifications
    modified_index: Optional[int]

    # Chat history
    chat_history: Annotated[List[Dict[str, str]], add]

    # AI response
    ai_response: Optional[str]

    # Error handling
    error: Optional[str]

    # Workflow control
    should_apply_edits: bool
    workflow_complete: bool


class LLMResponse(TypedDict):
    """Structured response from LLM parsing."""
    intent: str
    subtitle_edits: List[SubtitleEdit]
    response_message: str
    confidence: float
