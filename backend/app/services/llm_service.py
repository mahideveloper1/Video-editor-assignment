"""
LLM Service with LangGraph workflow for chat-based subtitle editing.
Orchestrates AI-powered subtitle generation and modification.
"""

from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END

# Import Google Gemini support
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from app.config import settings
from app.models.schemas import Subtitle, SubtitleStyle, ChatMessage, MessageType
from app.models.state import VideoEditState, SubtitleEdit, LLMResponse
from app.utils.helpers import parse_time_string, generate_id, color_name_to_hex
from app.utils.session import session_manager


class LLMService:
    """Service for LLM-powered subtitle editing using LangGraph."""

    def __init__(self):
        self.llm = self._initialize_llm()
        self.workflow = self._build_workflow()

    def _initialize_llm(self):
        """Initialize LLM based on configuration."""
        if settings.llm_provider == "openai":
            return ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.openai_api_key
            )
        elif settings.llm_provider == "anthropic":
            return ChatAnthropic(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.anthropic_api_key
            )
        elif settings.llm_provider == "google" or settings.llm_provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise ValueError(
                    "Google Gemini support not available. "
                    "Install with: pip install langchain-google-genai"
                )
            return ChatGoogleGenerativeAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                google_api_key=settings.google_api_key
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for subtitle editing."""
        workflow = StateGraph(VideoEditState)

        # Add nodes
        workflow.add_node("parse_intent", self._parse_intent_node)
        workflow.add_node("extract_parameters", self._extract_parameters_node)
        workflow.add_node("apply_edits", self._apply_edits_node)
        workflow.add_node("generate_response", self._generate_response_node)

        # Add edges
        workflow.set_entry_point("parse_intent")
        workflow.add_edge("parse_intent", "extract_parameters")
        workflow.add_edge("extract_parameters", "apply_edits")
        workflow.add_edge("apply_edits", "generate_response")
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    def _parse_intent_node(self, state: VideoEditState) -> VideoEditState:
        """
        Parse user intent from message.
        Determines if user wants to add, modify, or remove subtitles.
        """
        user_message = state["user_message"]

        # Create prompt for intent parsing
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a subtitle editing assistant. Analyze the user's message and determine their intent.

Possible intents:
- add_subtitle: User wants to add a new subtitle
- modify_style: User wants to change subtitle styling (font, size, color, position)
- remove_subtitle: User wants to remove a subtitle
- list_subtitles: User wants to see current subtitles
- clear_all: User wants to remove all subtitles
- help: User needs help

Respond with ONLY the intent name, nothing else."""),
            ("user", "{message}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"message": user_message})

        intent = response.content.strip().lower()

        state["intent"] = intent
        return state

    def _extract_parameters_node(self, state: VideoEditState) -> VideoEditState:
        """
        Extract subtitle parameters from user message using LLM.
        Extracts: text, start_time, end_time, font_family, font_size, font_color, position.
        """
        user_message = state["user_message"]
        intent = state["intent"]

        if intent not in ["add_subtitle", "modify_style"]:
            state["subtitle_edits"] = []
            state["should_apply_edits"] = False
            return state

        # Create prompt for parameter extraction
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a subtitle parameter extractor. Extract subtitle information from the user's message.

Extract the following parameters:
- text: The subtitle text (if adding new subtitle)
- start_time: Start time in seconds or time format (e.g., "5 seconds", "1:30", "0:00:05")
- end_time: End time in seconds or time format
- font_family: Font name (e.g., Arial, Helvetica, Roboto)
- font_size: Font size in pixels (12-72)
- font_color: Color name or hex (e.g., red, #FF0000, white)
- position: top, center, or bottom
- bold: true or false
- italic: true or false

Respond with ONLY a JSON object containing the extracted parameters. Use null for missing values.
Example: {{"text": "Hello", "start_time": "0", "end_time": "5", "font_color": "red", "font_size": 32}}"""),
            ("user", "{message}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"message": user_message})

        # Parse JSON response
        try:
            params = json.loads(response.content.strip())
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response.content)
            if json_match:
                params = json.loads(json_match.group())
            else:
                params = {}

        # Convert time strings to seconds and ensure valid values
        start_time = params.get("start_time")
        if start_time:
            start_time = parse_time_string(str(start_time))
        start_time = start_time if start_time is not None else 0.0

        end_time = params.get("end_time")
        if end_time:
            end_time = parse_time_string(str(end_time))

        # If no end_time provided, default to start_time + 3 seconds
        if end_time is None:
            end_time = start_time + 3.0

        # Ensure end_time is after start_time
        if end_time <= start_time:
            end_time = start_time + 3.0

        # Create subtitle edit
        subtitle_edit: SubtitleEdit = {
            "text": params.get("text") or "",
            "start_time": float(start_time),
            "end_time": float(end_time),
            "font_family": params.get("font_family"),
            "font_size": params.get("font_size"),
            "font_color": params.get("font_color"),
            "position": params.get("position"),
            "bold": params.get("bold"),
            "italic": params.get("italic")
        }

        state["subtitle_edits"] = [subtitle_edit]
        state["extracted_params"] = params
        state["should_apply_edits"] = True

        return state

    def _apply_edits_node(self, state: VideoEditState) -> VideoEditState:
        """Apply subtitle edits to the session."""
        if not state.get("should_apply_edits", False):
            return state

        session_id = state["session_id"]
        subtitle_edits = state.get("subtitle_edits", [])

        if not subtitle_edits:
            return state

        # Get current subtitles from session
        session = session_manager.get_session(session_id)
        if not session:
            state["error"] = "Session not found"
            return state

        current_subtitles = list(session.subtitles)

        # Apply each edit
        for edit in subtitle_edits:
            # Create new subtitle
            subtitle = Subtitle(
                id=generate_id("sub"),
                text=edit["text"],
                start_time=edit["start_time"],
                end_time=edit["end_time"],
                style=SubtitleStyle(
                    font_family=edit.get("font_family") or settings.default_font_family,
                    font_size=edit.get("font_size") or settings.default_font_size,
                    font_color=edit.get("font_color") or settings.default_font_color,
                    position=edit.get("position") or settings.default_subtitle_position,
                    bold=edit.get("bold") or False,
                    italic=edit.get("italic") or False
                )
            )
            current_subtitles.append(subtitle)

        # Update session with new subtitles
        session_manager.update_subtitles(session_id, current_subtitles)

        # Update state
        state["current_subtitles"] = [sub.model_dump() for sub in current_subtitles]

        return state

    def _generate_response_node(self, state: VideoEditState) -> VideoEditState:
        """Generate AI response based on the action taken."""
        intent = state.get("intent", "")
        subtitle_edits = state.get("subtitle_edits", [])
        error = state.get("error")

        if error:
            state["ai_response"] = f"Error: {error}"
            state["workflow_complete"] = True
            return state

        # Generate appropriate response based on intent
        if intent == "add_subtitle" and subtitle_edits:
            edit = subtitle_edits[0]
            response = (
                f"✓ Added subtitle: \"{edit['text']}\" "
                f"from {edit['start_time']:.1f}s to {edit['end_time']:.1f}s"
            )

            # Add styling info if specified
            style_parts = []
            if edit.get("font_color"):
                style_parts.append(f"color: {edit['font_color']}")
            if edit.get("font_size"):
                style_parts.append(f"size: {edit['font_size']}px")
            if edit.get("font_family"):
                style_parts.append(f"font: {edit['font_family']}")

            if style_parts:
                response += f" with {', '.join(style_parts)}"

            state["ai_response"] = response

        elif intent == "help":
            state["ai_response"] = """I can help you add and style subtitles! Here are some examples:

• "Add subtitle 'Hello World' from 0 to 5 seconds"
• "Add 'Welcome!' from 1:30 to 1:35 with red color"
• "Add subtitle 'Chapter 1' at 10 seconds for 5 seconds, size 48, bold"
• "Add 'The End' from 2 minutes to 2:10 with yellow color, Arial font"

I understand:
- Times: "5 seconds", "1:30", "2 minutes 30 seconds"
- Colors: red, blue, yellow, white, or hex codes like #FF0000
- Fonts: Arial, Helvetica, Roboto, etc.
- Sizes: 12-72 pixels
- Position: top, center, bottom
- Styles: bold, italic"""

        else:
            state["ai_response"] = "I'm ready to help you add subtitles!"

        state["workflow_complete"] = True
        return state

    async def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Process user message through LangGraph workflow.

        Args:
            session_id: Video editing session ID
            user_message: User's chat message

        Returns:
            Dictionary with AI response and updated subtitles
        """
        # Get current session
        session = session_manager.get_session(session_id)
        if not session:
            return {
                "error": "Session not found or expired",
                "ai_response": "Session not found. Please upload a video first.",
                "subtitles": []
            }

        # Get chat history
        chat_history = session_manager.get_chat_history(session_id)

        # Initialize state
        initial_state: VideoEditState = {
            "session_id": session_id,
            "user_message": user_message,
            "intent": None,
            "extracted_params": None,
            "current_subtitles": [sub.model_dump() for sub in session.subtitles],
            "subtitle_edits": None,
            "chat_history": [
                {"role": msg.type.value, "content": msg.content}
                for msg in chat_history
            ],
            "ai_response": None,
            "error": None,
            "should_apply_edits": False,
            "workflow_complete": False
        }

        # Run workflow
        try:
            final_state = self.workflow.invoke(initial_state)
        except Exception as e:
            return {
                "error": str(e),
                "ai_response": f"Sorry, I encountered an error: {str(e)}",
                "subtitles": [sub.model_dump() for sub in session.subtitles]
            }

        # Save chat messages
        user_chat_msg = ChatMessage(
            type=MessageType.USER,
            content=user_message,
            timestamp=datetime.now()
        )
        session_manager.add_chat_message(session_id, user_chat_msg)

        ai_chat_msg = ChatMessage(
            type=MessageType.AI,
            content=final_state["ai_response"] or "Done!",
            timestamp=datetime.now(),
            metadata=final_state.get("extracted_params")
        )
        session_manager.add_chat_message(session_id, ai_chat_msg)

        # Get updated subtitles
        updated_session = session_manager.get_session(session_id)
        subtitles = updated_session.subtitles if updated_session else []

        return {
            "ai_response": final_state.get("ai_response", "Done!"),
            "subtitles": [sub.model_dump() for sub in subtitles],
            "intent": final_state.get("intent"),
            "extracted_params": final_state.get("extracted_params")
        }


# Global LLM service instance
llm_service = LLMService()
