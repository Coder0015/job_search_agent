from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from app.api.routes.health import health_router
from app.api.routes.resumes import resume_router
from app.api.routes.jobs import job_router
from app.api.routes.chat import chat_router
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.job_service import JobService
from app.services.chat_service import ChatService
from app.services.session_service import SessionService
from langgraph.checkpoint.memory import MemorySaver
from app.agents.factory.deepseek_agent import create_job_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时初始化共享数据资源。"""

    print("正在加载简历数据...")
    app.state.resume_repository = ResumeRepository()
    print("正在加载招聘岗位数据...")
    app.state.job_repository = JobRepository()
    app.state.job_service = JobService(
        app.state.job_repository
    )
    print("简历和岗位数据加载完成")

    print("正在创建求职助手...")
    app.state.checkpointer = MemorySaver()
    app.state.agent = create_job_agent(
        job_service=app.state.job_service,
        checkpointer=app.state.checkpointer,
    )
    app.state.session_service = SessionService()
    app.state.chat_service = ChatService(
        session_service=app.state.session_service,
        resume_repository=app.state.resume_repository,
        agent=app.state.agent,
    )

    yield


app = FastAPI(
    title="AI_Job",
    description="面向求职岗位推荐的 AI 求职助手demo",
    version="0.1.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse("app/static/index.html")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    prefix="/api",
    tags=["health"],
)
app.include_router(
    resume_router,
    prefix="/api/resumes",
    tags=["resumes"],
)
app.include_router(
    job_router,
    prefix="/api/jobs",
    tags=["jobs"],
)
app.include_router(
    chat_router,
    prefix="/api/chat",
    tags=["chat"],
)
if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, reload=True, host="localhost")
