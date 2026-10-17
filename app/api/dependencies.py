from fastapi import Request
from app.agents.factory.agent_provider import AgentProvider
from app.repositories.resume_repository import ResumeRepository

from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService
from app.services.chat_service import ChatService
from app.services.session_service import SessionService


def get_resume_repository(
        request: Request,
) -> ResumeRepository:
    return request.app.state.resume_repository


def get_job_repository(
        request: Request,
) -> JobRepository:
    return request.app.state.job_repository


def get_job_service(
        request: Request,
) -> JobService:
    return request.app.state.job_service


def get_session_service(request: Request) -> SessionService:
    return request.app.state.session_service


def get_agent_provider(request: Request) -> AgentProvider:
    return request.app.state.agent_provider


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service
