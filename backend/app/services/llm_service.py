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
        session_id = state["session_id"]

        # Get current subtitles for context
        session = session_manager.get_session(session_id)
        current_subtitles = []
        if session:
            current_subtitles = [
                f"Subtitle {i+1}: \"{sub.text}\" from {sub.start_time}s to {sub.end_time}s"
                for i, sub in enumerate(session.subtitles)
            ]

        # Create prompt for intent parsing
        context = "\n".join(current_subtitles) if current_subtitles else "No subtitles yet"

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a subtitle editing assistant. Analyze the user's message and determine their intent.

Current subtitles:
{context}

Possible intents:
- add_subtitle: User wants to add a NEW subtitle (e.g., "add 'hello' at 5 seconds")
- modify_subtitle: User wants to CHANGE an existing subtitle's text, time, or style (e.g., "make the previous subtitle red", "change the last one to blue", "make subtitle 1 bigger")
- remove_subtitle: User wants to remove a subtitle
- list_subtitles: User wants to see current subtitles
- clear_all: User wants to remove all subtitles
- help: User needs help

IMPORTANT: If user mentions "previous", "last", "that", "this", or references an existing subtitle number, use "modify_subtitle".

Respond with ONLY the intent name, nothing else."""),
            ("user", "{message}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"message": user_message, "context": context})

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
        session_id = state["session_id"]

        if intent not in ["add_subtitle", "modify_subtitle", "modify_style"]:
            state["subtitle_edits"] = []
            state["should_apply_edits"] = False
            return state

        # Get current subtitles for context
        session = session_manager.get_session(session_id)
        current_subtitles = []
        if session:
            current_subtitles = [
                f"Subtitle {i+1}: \"{sub.text}\" from {sub.start_time}s to {sub.end_time}s, color: {sub.style.font_color}, size: {sub.style.font_size}"
                for i, sub in enumerate(session.subtitles)
            ]

        context = "\n".join(current_subtitles) if current_subtitles else "No subtitles yet"

        # Create prompt for parameter extraction
        if intent == "modify_subtitle":
            system_message = """You are a subtitle parameter extractor. Extract which subtitle to modify and what changes to make.

Current subtitles:
{context}

Extract the following parameters:
- subtitle_index: Which subtitle to modify (use -1 for last/previous/most recent, or specific number like 0, 1, 2). REQUIRED for modifications.
- text: New subtitle text (only if user wants to change the text)
- start_time: New start time (only if user wants to change timing)
- end_time: New end time (only if user wants to change timing)
- font_family: New font name (only if user wants to change font)
- font_size: New font size in pixels (only if user wants to change size)
- font_color: New color name or hex (only if user wants to change color)
- position: New position - top, center, or bottom (only if user wants to change position)
- bold: true or false (only if user mentions bold)
- italic: true or false (only if user mentions italic)

IMPORTANT:
- For "previous", "last", or "that subtitle", use subtitle_index: -1
- For "subtitle 1" or "first subtitle", use subtitle_index: 0
- For "subtitle 2", use subtitle_index: 1
- Only include parameters that the user wants to CHANGE, use null for others

Respond with ONLY a JSON object.
Example: {{"subtitle_index": -1, "font_color": "red"}} for "make the previous subtitle red"
Example: {{"subtitle_index": 0, "font_size": 48}} for "make subtitle 1 bigger" """
        else:
            system_message = """You are a subtitle parameter extractor. Extract subtitle information from the user's message.

Extract the following parameters:
- text: The subtitle text (REQUIRED for new subtitles)
- start_time: Start time in seconds or time format (e.g., "5 seconds", "1:30", "0:00:05")
- end_time: End time in seconds or time format
- font_family: Font name (e.g., Arial, Helvetica, Roboto)
- font_size: Font size in pixels (12-72)
- font_color: Color name or hex (e.g., red, #FF0000, white)
- position: top, center, or bottom
- bold: true or false
- italic: true or false

Respond with ONLY a JSON object containing the extracted parameters. Use null for missing values.
Example: {{"text": "Hello", "start_time": "0", "end_time": "5", "font_color": "red", "font_size": 32}}"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("user", "{message}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"message": user_message, "context": context})

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

        # Handle modification vs addition
        if intent == "modify_subtitle":
            # For modifications, preserve nulls to indicate unchanged fields
            subtitle_edit: SubtitleEdit = {
                "subtitle_index": params.get("subtitle_index", -1),  # Default to last subtitle
                "text": params.get("text"),
                "start_time": None,
                "end_time": None,
                "font_family": params.get("font_family"),
                "font_size": params.get("font_size"),
                "font_color": params.get("font_color"),
                "position": params.get("position"),
                "bold": params.get("bold"),
                "italic": params.get("italic")
            }

            # Only parse times if they're specified
            if params.get("start_time") is not None:
                subtitle_edit["start_time"] = parse_time_string(str(params["start_time"]))
            if params.get("end_time") is not None:
                subtitle_edit["end_time"] = parse_time_string(str(params["end_time"]))

        else:
            # For new subtitles, parse times and apply defaults
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

            # Create subtitle edit for new subtitle
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
        intent = state.get("intent", "")

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
            # Check if this is a modification or addition
            if "subtitle_index" in edit and edit["subtitle_index"] is not None:
                # MODIFY existing subtitle
                index = edit["subtitle_index"]

                # Handle negative index (e.g., -1 for last subtitle)
                if index < 0:
                    index = len(current_subtitles) + index

                # Validate index
                if index < 0 or index >= len(current_subtitles):
                    state["error"] = f"Invalid subtitle index: {edit['subtitle_index']}"
                    return state

                # Get existing subtitle
                existing = current_subtitles[index]

                # Update only the fields that are specified (not None)
                updated_style = SubtitleStyle(
                    font_family=edit.get("font_family") if edit.get("font_family") is not None else existing.style.font_family,
                    font_size=edit.get("font_size") if edit.get("font_size") is not None else existing.style.font_size,
                    font_color=edit.get("font_color") if edit.get("font_color") is not None else existing.style.font_color,
                    position=edit.get("position") if edit.get("position") is not None else existing.style.position,
                    bold=edit.get("bold") if edit.get("bold") is not None else existing.style.bold,
                    italic=edit.get("italic") if edit.get("italic") is not None else existing.style.italic
                )

                # Create modified subtitle
                modified_subtitle = Subtitle(
                    id=existing.id,  # Keep same ID
                    text=edit.get("text") if edit.get("text") is not None else existing.text,
                    start_time=edit.get("start_time") if edit.get("start_time") is not None else existing.start_time,
                    end_time=edit.get("end_time") if edit.get("end_time") is not None else existing.end_time,
                    style=updated_style
                )

                # Replace the subtitle at this index
                current_subtitles[index] = modified_subtitle
                state["modified_index"] = index  # Track which subtitle was modified

            else:
                # ADD new subtitle
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

        # Update session with modified/new subtitles
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

        elif intent == "modify_subtitle" and subtitle_edits:
            edit = subtitle_edits[0]
            modified_index = state.get("modified_index", 0)

            # Build response showing what was modified
            changes = []
            if edit.get("text") is not None:
                changes.append(f"text to \"{edit['text']}\"")
            if edit.get("font_color") is not None:
                changes.append(f"color to {edit['font_color']}")
            if edit.get("font_size") is not None:
                changes.append(f"size to {edit['font_size']}px")
            if edit.get("font_family") is not None:
                changes.append(f"font to {edit['font_family']}")
            if edit.get("position") is not None:
                changes.append(f"position to {edit['position']}")
            if edit.get("bold") is not None:
                changes.append("bold" if edit["bold"] else "not bold")
            if edit.get("italic") is not None:
                changes.append("italic" if edit["italic"] else "not italic")

            response = f"✓ Modified subtitle {modified_index + 1}"
            if changes:
                response += f": changed {', '.join(changes)}"

            state["ai_response"] = response

        elif intent == "help":
            state["ai_response"] = """I can help you add and modify subtitles! Here are some examples:

**Adding subtitles:**
• "Add subtitle 'Hello World' from 0 to 5 seconds"
• "Add 'Welcome!' from 1:30 to 1:35 with red color"
• "Add subtitle 'Chapter 1' at 10 seconds, size 48, bold"

**Modifying subtitles:**
• "Make the previous subtitle red"
• "Change the last subtitle to blue"
• "Make subtitle 1 bigger"
• "Change the last one to size 36"

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
