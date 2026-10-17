from langchain.agents import create_agent
from langgraph.checkpoint.base import BaseCheckpointSaver

from app.agents.model.deepseek import create_deepseek_model
from app.agents.prompts.job_prompts import build_system_prompt
from app.agents.tools.search_jobs import create_search_job

from app.services.job_service import JobService


def create_job_agent(
    job_service: JobService,
    checkpointer: BaseCheckpointSaver,
    resume_context: str | None = None,
):
    """创建求职 Agent，可注入当前求职者简历上下文。"""
    llm = create_deepseek_model()
    tools = create_search_job(job_service)

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=build_system_prompt(resume_context),
        checkpointer=checkpointer,
    )

    return agent