"""Session persistence service for saving and loading golf rounds."""
import json
from pathlib import Path
from typing import List, Optional

from src.lib.exceptions import ServiceError
from src.models.session import Session
from src.models.shot_event import ShotEvent


class SessionService:
    """
    Session persistence service.

    Saves and loads golf round sessions with shot history.
    """

    def __init__(self, sessions_dir: str = "data/sessions"):
        """
        Initialize session service.

        Args:
            sessions_dir: Directory for session storage
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session: Session) -> None:
        """
        Save session to disk.

        Args:
            session: Session to save

        Raises:
            ServiceError: If save fails
        """
        try:
            session_file = self.sessions_dir / f"{session.id}.json"

            # Convert to dict
            session_data = session.to_dict()

            # Add shot events (without screenshots)
            session_data["shot_events"] = [
                shot.to_dict() for shot in session.shot_events
            ]

            # Write to file
            with open(session_file, "w") as f:
                json.dump(session_data, f, indent=2)

        except Exception as e:
            raise ServiceError(f"Failed to save session: {e}")

    def load_session(self, session_id: str) -> Optional[Session]:
        """
        Load session from disk.

        Args:
            session_id: Session ID to load

        Returns:
            Session instance or None if not found

        Raises:
            ServiceError: If load fails
        """
        try:
            session_file = self.sessions_dir / f"{session_id}.json"

            if not session_file.exists():
                return None

            with open(session_file, "r") as f:
                session_data = json.load(f)

            # Load shot events (without screenshots)
            shot_events = [
                ShotEvent.from_dict(shot_data)
                for shot_data in session_data.get("shot_events", [])
            ]

            # Create session
            session = Session.from_dict(session_data, shot_events=shot_events)

            return session

        except Exception as e:
            raise ServiceError(f"Failed to load session: {e}")

    def list_sessions(self) -> List[dict]:
        """
        List all saved sessions.

        Returns:
            List of session summaries (id, start_time, total_shots)
        """
        sessions = []

        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, "r") as f:
                    data = json.load(f)

                sessions.append(
                    {
                        "id": data["id"],
                        "start_time": data["start_time"],
                        "end_time": data.get("end_time"),
                        "personality_name": data.get("personality_name", "unknown"),
                        "total_shots": data.get("total_shots", 0),
                        "total_cost": data.get("total_cost", 0.0),
                    }
                )
            except Exception:
                # Skip invalid files
                continue

        # Sort by start time (most recent first)
        sessions.sort(key=lambda x: x["start_time"], reverse=True)

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        if session_file.exists():
            session_file.unlink()
            return True

        return False

    def get_session_stats(self) -> dict:
        """
        Get aggregate statistics across all sessions.

        Returns:
            Dictionary with total sessions, shots, cost, etc.
        """
        sessions = self.list_sessions()

        total_sessions = len(sessions)
        total_shots = sum(s["total_shots"] for s in sessions)
        total_cost = sum(s["total_cost"] for s in sessions)

        return {
            "total_sessions": total_sessions,
            "total_shots": total_shots,
            "total_cost": total_cost,
            "avg_shots_per_session": total_shots / total_sessions if total_sessions > 0 else 0,
            "avg_cost_per_session": total_cost / total_sessions if total_sessions > 0 else 0,
        }
