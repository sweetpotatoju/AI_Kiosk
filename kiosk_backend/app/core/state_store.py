from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class KioskState:
    current_state: str = "IDLE"
    session_id: Optional[str] = None
    greeted: bool = False
    last_detected_at: Optional[str] = None
    message_text: Optional[str] = None
    user_text: Optional[str] = None


class StateStore:
    def __init__(self) -> None:
        self._state = KioskState()

    def get_state(self) -> dict:
        return asdict(self._state)

    def handle_detection(self, detected: bool) -> dict:
        now = datetime.now().isoformat(timespec="seconds")

        if not detected:
            return {
                "success": True,
                "message": "no user detected",
                "state": self._state.current_state,
                "session_id": self._state.session_id,
            }

        # IDLE일 때만 새로운 감지 허용
        if self._state.current_state != "IDLE":
            return {
                "success": True,
                "message": "ignored detection (already active)",
                "state": self._state.current_state,
                "session_id": self._state.session_id,
            }

        self._state.current_state = "USER_DETECTED"
        self._state.session_id = str(uuid4())
        self._state.greeted = False
        self._state.last_detected_at = now
        self._state.message_text = None

        return {
            "success": True,
            "message": "user detected, state changed",
            "state": self._state.current_state,
            "session_id": self._state.session_id,
            "last_detected_at": self._state.last_detected_at,
        }

    def start_greeting(self) -> dict:
        if self._state.greeted:
            return {
                "success": True,
                "message": "already greeted",
                "state": self._state.current_state,
                "session_id": self._state.session_id,
                "message_text": self._state.message_text,
            }

        if self._state.current_state != "USER_DETECTED":
            return {
                "success": False,
                "message": "greeting cannot start in current state",
                "state": self._state.current_state,
                "session_id": self._state.session_id,
            }

        self._state.current_state = "GREETING"
        self._state.greeted = True
        self._state.message_text = "안녕하세요. 무엇을 도와드릴까요?"
        self._state.last_detected_at = datetime.now().isoformat(timespec="seconds")

        return {
            "success": True,
            "message": "greeting started",
            "state": self._state.current_state,
            "session_id": self._state.session_id,
            "message_text": self._state.message_text,
            "tts_text": self._state.message_text,
        }

    def start_listening(self) -> dict:
        if self._state.current_state == "LISTENING":
            return {
                "success": True,
                "message": "already listening",
                "state": self._state.current_state,
                "session_id": self._state.session_id,
                "message_text": self._state.message_text,
            }

        if self._state.current_state != "GREETING":
            return {
                "success": False,
                "message": "cannot start listening in current state",
                "state": self._state.current_state,
            }

        self._state.current_state = "LISTENING"
        self._state.message_text = "말씀해주세요."
        self._state.last_detected_at = datetime.now().isoformat(timespec="seconds")

        return {
            "success": True,
            "message": "listening started",
            "state": self._state.current_state,
            "session_id": self._state.session_id,
            "message_text": self._state.message_text,
        }

    def start_processing(self, user_text: str) -> dict:
        if self._state.current_state != "LISTENING":
            return {
                "success": False,
                "message": "not in listening state",
                "state": self._state.current_state,
            }
        self._state.current_state = "PROCESSING"
        self._state.user_text = user_text
        self._state.message_text = "답변을 생각하는 중..."
        return {"success": True, "state": self._state.current_state}

    def start_responding(self, answer_text: str) -> dict:
        if self._state.current_state != "PROCESSING":
            return {
                "success": False,
                "message": "not in processing state",
                "state": self._state.current_state,
            }
        self._state.current_state = "RESPONDING"
        self._state.message_text = answer_text
        return {"success": True, "state": self._state.current_state}

    def back_to_listening(self) -> dict:
        if self._state.current_state != "RESPONDING":
            return {
                "success": False,
                "message": "not in responding state",
                "state": self._state.current_state,
            }
        self._state.current_state = "LISTENING"
        self._state.user_text = None
        self._state.message_text = "말씀해주세요."
        return {"success": True, "state": self._state.current_state}

    def touch_presence(self) -> None:
        """사람이 아직 존재한다고 판단될 때 시간만 갱신"""
        self._state.last_detected_at = datetime.now().isoformat(timespec="seconds")

    def check_timeout(self, timeout_seconds: int = 10) -> dict | None:
        if self._state.current_state == "IDLE":
            return None

        if not self._state.last_detected_at:
            return None

        last_time = datetime.fromisoformat(self._state.last_detected_at)
        now = datetime.now()

        if (now - last_time).total_seconds() > timeout_seconds:
            return self.reset()

        return None

    def reset(self) -> dict:
        self._state = KioskState()
        return {
            "success": True,
            "message": "state reset completed",
            "state": self._state.current_state,
        }


state_store = StateStore()