import json
from dataclasses import dataclass
from typing import Any, Generator

from app.repositories.resume_repository import ResumeRepository
from app.services.session_service import SessionService


@dataclass(frozen=True)
class ChatResult:
    """一次聊天调用的结构化结果，供后续 API 层转换为响应模型。"""

    session_id: str
    resume_id: str
    reply: str
    jobs: list[dict[str, Any]]


class ChatService:
    """连接会话、简历和 Agent 的聊天业务服务。"""

    def __init__(
        self,
        session_service: SessionService,
        resume_repository: ResumeRepository,
        agent_provider: Any,
        checkpointer: Any,
    ):
        self.session_service = session_service
        self.resume_repository = resume_repository
        # 按 resume_id 懒加载 Agent，系统提示词中已注入对应简历。
        self.agent_provider = agent_provider
        # 会话关闭时需要同时清除对应的对话历史。
        self.checkpointer = checkpointer

    def close_session(self, session_id: str) -> None:
        """彻底关闭会话：删除会话、对话历史和缓存的 Agent。

        切换简历后旧对话不应残留；再次选择同一份简历应开始全新对话。
        """
        session = self.session_service.get_session(session_id)
        if session is None:
            raise ValueError("会话不存在或已过期")

        self.session_service.delete_session(session_id)
        self.checkpointer.delete_thread(session.thread_id)
        self.agent_provider.invalidate(session.resume_id)

    def chat(self, session_id: str, message: str) -> ChatResult:
        """使用指定会话调用 Agent，并提取本轮岗位工具结果。"""
        cleaned_message = message.strip()
        if not cleaned_message:
            raise ValueError("聊天消息不能为空")

        session = self.session_service.get_session(session_id)
        if session is None:
            raise ValueError("会话不存在或已过期")

        resume = self.resume_repository.get_by_id(session.resume_id)
        if resume is None:
            raise ValueError("会话绑定的简历不存在")

        agent = self._get_agent(session.resume_id)

        state_before = agent.get_state(
            {"configurable": {"thread_id": session.thread_id}}
        )
        message_count_before = len(
            state_before.values.get("messages", [])
        )

        prompt = self._build_user_message(resume, cleaned_message)
        result = agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config={"configurable": {"thread_id": session.thread_id}},
        )

        messages = result.get("messages", [])
        new_messages = messages[message_count_before:]
        if not new_messages:
            raise ValueError("Agent 没有返回消息")

        reply = self._extract_reply(messages)
        jobs = self._extract_jobs(new_messages)

        return ChatResult(
            session_id=session.session_id,
            resume_id=session.resume_id,
            reply=reply,
            jobs=jobs,
        )

    def chat_stream(
        self, session_id: str, message: str
    ) -> Generator[str, None, None]:
        """流式调用 Agent，yield SSE 格式的数据行。

        每个文本 token：data: {"type":"token","content":"..."}
        工具岗位结果： data: {"type":"jobs","jobs":[...]}
        结束：        data: {"type":"done"}
        出错：        data: {"type":"error","message":"..."}
        """
        cleaned_message = message.strip()
        if not cleaned_message:
            yield _sse({"type": "error", "message": "聊天消息不能为空"})
            return

        session = self.session_service.get_session(session_id)
        if session is None:
            yield _sse({"type": "error", "message": "会话不存在或已过期"})
            return

        resume = self.resume_repository.get_by_id(session.resume_id)
        if resume is None:
            yield _sse({"type": "error", "message": "会话绑定的简历不存在"})
            return

        try:
            agent = self._get_agent(session.resume_id)
        except ValueError as exc:
            yield _sse({"type": "error", "message": str(exc)})
            return

        prompt = self._build_user_message(resume, cleaned_message)
        config = {"configurable": {"thread_id": session.thread_id}}

        jobs: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        try:
            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": prompt}]},
                config=config,
                stream_mode="messages",
            ):
                # chunk 是 (message_chunk, metadata) 元组
                if not isinstance(chunk, tuple):
                    continue
                msg, _ = chunk
                msg_type = getattr(msg, "type", None)

                # AI token chunk：content 是逐 token 的文字片段
                if msg_type == "AIMessageChunk":
                    content = msg.content
                    if isinstance(content, str) and content:
                        yield _sse({"type": "token", "content": content})

                # 工具返回：收集岗位
                elif msg_type == "tool":
                    try:
                        payload = json.loads(msg.content)
                        for job in payload.get("jobs", []):
                            job_id = job.get("id")
                            if isinstance(job_id, str) and job_id not in seen_ids:
                                seen_ids.add(job_id)
                                jobs.append(job)
                    except (TypeError, json.JSONDecodeError):
                        pass

        except Exception as exc:
            yield _sse({"type": "error", "message": f"模型调用失败：{exc}"})
            return

        if jobs:
            yield _sse({"type": "jobs", "jobs": jobs})

        yield _sse({"type": "done"})

    def _get_agent(self, resume_id: str) -> Any:
        """获取绑定了指定简历上下文的 Agent（不存在时自动创建）。"""
        return self.agent_provider.get_agent(resume_id)

    @staticmethod
    def _build_user_message(resume, message: str) -> str:
        return message

    @staticmethod
    def _extract_reply(messages: list[Any]) -> str:
        for message in reversed(messages):
            if getattr(message, "type", None) == "ai":
                content = message.content
                if isinstance(content, str) and content.strip():
                    return content.strip()
        raise ValueError("Agent 没有返回文本回复")

    @staticmethod
    def _extract_jobs(messages: list[Any]) -> list[dict[str, Any]]:
        jobs: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        for message in messages:
            if getattr(message, "type", None) != "tool":
                continue
            try:
                payload = json.loads(message.content)
            except (TypeError, json.JSONDecodeError):
                continue
            for job in payload.get("jobs", []):
                if not isinstance(job, dict):
                    continue
                job_id = job.get("id")
                if not isinstance(job_id, str) or job_id in seen_ids:
                    continue
                seen_ids.add(job_id)
                jobs.append(job)

        return jobs


def _sse(data: dict) -> str:
    """将字典序列化为 SSE data 行，以双换行结尾。"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

