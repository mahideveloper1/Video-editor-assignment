"""
Session management for video editing sessions.
In-memory storage with TTL support.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path

from app.models.schemas import VideoSession, Subtitle, ChatMessage
from app.config import settings


class SessionManager:
    """Manages video editing sessions with TTL support."""

    def __init__(self):
        self._sessions: Dict[str, VideoSession] = {}
        self._chat_history: Dict[str, List[ChatMessage]] = {}
        self._session_timestamps: Dict[str, datetime] = {}

    def create_session(
        self,
        video_path: str,
        metadata: dict
    ) -> VideoSession:
        """Create a new video editing session."""
        session_id = f"sess_{uuid.uuid4().hex[:16]}"

        session = VideoSession(
            session_id=session_id,
            video_path=video_path,
            metadata=metadata,
            subtitles=[],
            created_at=datetime.now()
        )

        self._sessions[session_id] = session
        self._chat_history[session_id] = []
        self._session_timestamps[session_id] = datetime.now()

        return session

    def get_session(self, session_id: str) -> Optional[VideoSession]:
        """Get session by ID, returns None if not found or expired."""
        self._cleanup_expired_sessions()

        if session_id not in self._sessions:
            return None

        # Update last access timestamp
        self._session_timestamps[session_id] = datetime.now()

        return self._sessions[session_id]

    def update_subtitles(
        self,
        session_id: str,
        subtitles: List[Subtitle]
    ) -> bool:
        """Update subtitles for a session."""
        session = self.get_session(session_id)
        if not session:
            return False

        session.subtitles = subtitles
        return True

    def add_subtitle(
        self,
        session_id: str,
        subtitle: Subtitle
    ) -> bool:
        """Add a subtitle to session."""
        session = self.get_session(session_id)
        if not session:
            return False

        session.subtitles.append(subtitle)
        return True

    def get_subtitles(self, session_id: str) -> Optional[List[Subtitle]]:
        """Get all subtitles for a session."""
        session = self.get_session(session_id)
        if not session:
            return None

        return session.subtitles

    def add_chat_message(
        self,
        session_id: str,
        message: ChatMessage
    ) -> bool:
        """Add a chat message to session history."""
        if session_id not in self._chat_history:
            return False

        self._chat_history[session_id].append(message)
        return True

    def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """Get chat history for a session."""
        return self._chat_history.get(session_id, [])

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its associated data."""
        if session_id not in self._sessions:
            return False

        # Get video path for cleanup
        session = self._sessions[session_id]

        # Delete session data
        del self._sessions[session_id]
        del self._chat_history[session_id]
        del self._session_timestamps[session_id]

        # Clean up files (optional - can be done async)
        try:
            video_path = Path(session.video_path)
            if video_path.exists():
                video_path.unlink()
        except Exception as e:
            print(f"Error deleting video file: {e}")

        return True

    def _cleanup_expired_sessions(self):
        """Remove expired sessions based on TTL."""
        now = datetime.now()
        expired_sessions = []

        for session_id, timestamp in self._session_timestamps.items():
            if now - timestamp > timedelta(seconds=settings.session_ttl):
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            print(f"Cleaning up expired session: {session_id}")
            self.delete_session(session_id)

    def get_all_sessions(self) -> Dict[str, VideoSession]:
        """Get all active sessions (for debugging)."""
        self._cleanup_expired_sessions()
        return self._sessions.copy()

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists and is not expired."""
        return self.get_session(session_id) is not None


# Global session manager instance
session_manager = SessionManager()
