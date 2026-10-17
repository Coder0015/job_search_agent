from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse

from app.agents.factory.agent_provider import AgentProvider
from app.api.dependencies import (
    get_agent_provider,
    get_chat_service,
    get_resume_repository,
    get_session_service,
)
from app.repositories.resume_repository import ResumeRepository
from app.schemas.chat import ChatRequest, ChatResponse, CreateSessionRequest, CreateSessionResponse
from app.services.chat_service import ChatService
from app.services.session_service import SessionService


chat_router = APIRouter()


@chat_router.post("/sessions", response_model=CreateSessionResponse)
def create_chat_session(
    request: CreateSessionRequest,
    resume_repository: ResumeRepository = Depends(get_resume_repository),
    session_service: SessionService = Depends(get_session_service),
    agent_provider: AgentProvider = Depends(get_agent_provider),
) -> CreateSessionResponse:
    """创建绑定指定简历的聊天会话，并按需创建该简历的 Agent。"""
    if resume_repository.get_by_id(request.resume_id) is None:
        raise HTTPException(status_code=404, detail="未找到对应的求职者简历")

    # 选定简历后再创建 Agent，避免应用启动时预先构建所有简历的 Agent。
    agent_provider.get_agent(request.resume_id)

    session = session_service.create_session(request.resume_id)
    return CreateSessionResponse(
        session_id=session.session_id,
        resume_id=session.resume_id,
    )


@chat_router.delete("/sessions/{session_id}", status_code=204)
def delete_chat_session(
    session_id: str,
    service: ChatService = Depends(get_chat_service),
) -> Response:
    """关闭会话，同时清除对话历史和缓存的 Agent。"""
    try:
        service.close_session(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=204)


@chat_router.post("", response_model=ChatResponse)
def send_chat_message(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """向指定聊天会话发送一条消息（非流式）。"""
    try:
        result = service.chat(request.session_id, request.message)
    except ValueError as exc:
        detail = str(exc)
        status_code = 404 if "会话" in detail or "简历" in detail else 400
        raise HTTPException(status_code=status_code, detail=detail) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="求职助手暂时无法回复，请稍后重试") from exc

    return ChatResponse(
        session_id=result.session_id,
        resume_id=result.resume_id,
        reply=result.reply,
        jobs=result.jobs,
    )


@chat_router.post("/stream")
def send_chat_message_stream(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    """向指定聊天会话发送一条消息（SSE 流式）。

    每条 SSE 数据格式为 JSON：
    - {"type":"token","content":"..."} — AI 文本片段
    - {"type":"jobs","jobs":[...]}     — 工具查询到的岗位（流结束前）
    - {"type":"done"}                  — 流正常结束
    - {"type":"error","message":"..."} — 出错
    """
    return StreamingResponse(
        service.chat_stream(request.session_id, request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

