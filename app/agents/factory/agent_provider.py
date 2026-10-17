from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver

from app.agents.factory.deepseek_agent import create_job_agent
from app.agents.prompts.resume_context import format_resume_context
from app.repositories.resume_repository import ResumeRepository
from app.services.job_service import JobService


class AgentProvider:
    """按简历懒加载并缓存求职 Agent。

    每个 Agent 的系统提示词中注入对应求职者的简历。
    首次为某份简历创建会话时构建 Agent，之后复用缓存；
    新增简历不需要修改代码，选择简历时会自动创建。
    """

    def __init__(
        self,
        job_service: JobService,
        resume_repository: ResumeRepository,
        checkpointer: BaseCheckpointSaver,
    ):
        self.job_service = job_service
        self.resume_repository = resume_repository
        self.checkpointer = checkpointer
        self._agents: dict[str, Any] = {}

    def get_agent(self, resume_id: str) -> Any:
        """获取指定简历对应的 Agent，不存在时创建并缓存。"""
        cached = self._agents.get(resume_id)
        if cached is not None:
            return cached

        resume = self.resume_repository.get_by_id(resume_id)
        if resume is None:
            raise ValueError("未找到对应的求职者简历")

        agent = create_job_agent(
            job_service=self.job_service,
            checkpointer=self.checkpointer,
            resume_context=format_resume_context(resume),
        )
        self._agents[resume_id] = agent
        return agent

    def invalidate(self, resume_id: str) -> None:
        """丢弃指定简历缓存的 Agent，下次使用时重新创建。"""
        self._agents.pop(resume_id, None)
