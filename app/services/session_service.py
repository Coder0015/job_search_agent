from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class Session:
    """一次求职对话的服务端会话记录。"""

    session_id: str
    resume_id: str
    thread_id: str
    created_at: datetime


class SessionService:
    """管理内存中的会话及其简历、Agent 线程绑定。"""

    def __init__(self):
        self._sessions: dict[str, Session] = {}

    def create_session(self, resume_id: str) -> Session:
        """创建绑定指定简历的独立会话。"""
        session_id = str(uuid4())
        session = Session(
            session_id=session_id,
            resume_id=resume_id,
            thread_id=f"session-{session_id}",
            created_at=datetime.now(timezone.utc),
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Session | None:
        """按会话 ID 查询会话，不存在时返回 None。"""
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> None:
        """删除会话；重复删除不会报错。"""
        self._sessions.pop(session_id, None)
