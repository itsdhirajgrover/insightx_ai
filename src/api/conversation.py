import time
import uuid
from typing import Dict, Any, Optional


class ConversationManager:
    """Simple in-memory conversation store for session context."""

    def __init__(self, ttl_seconds: int = 3600):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds

    def create_session(self) -> str:
        sid = str(uuid.uuid4())
        self.sessions[sid] = {
            "created_at": time.time(),
            "updated_at": time.time(),
            "last_intent": None,
            "last_entities": {},
            "history": []
        }
        return sid

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        s = self.sessions.get(session_id)
        if not s:
            return None
        # expire old sessions
        if time.time() - s["updated_at"] > self.ttl:
            del self.sessions[session_id]
            return None
        return s

    def update_session(self, session_id: str, intent: str, entities: Dict[str, Any], result: Dict[str, Any]):
        s = self.sessions.get(session_id)
        if not s:
            # create if missing
            session_id = self.create_session()
            s = self.sessions[session_id]
        s["last_intent"] = intent
        # merge entities
        s["last_entities"].update(entities or {})
        s["history"].append({"time": time.time(), "intent": intent, "entities": entities, "result_summary": result.get("insight")})
        s["updated_at"] = time.time()

    def merge_entities(self, session_id: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        s = self.get_session(session_id)
        if not s:
            return entities or {}
        merged = dict(s.get("last_entities", {}))
        merged.update(entities or {})
        return merged
