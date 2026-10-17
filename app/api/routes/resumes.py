from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_resume_repository
from app.schemas.resume import Resume
from app.repositories.resume_repository import ResumeRepository

resume_router = APIRouter()


@resume_router.get("/", response_model=list[Resume])
def list_resumes(
        repository: ResumeRepository = Depends(get_resume_repository),
) -> list[Resume]:
    """获取所有预置求职者。"""
    return repository.list_all()


@resume_router.get("/{resume_id}", response_model=Resume)
def get_resume(
        resume_id: str,
        repository: ResumeRepository = Depends(get_resume_repository),
) -> Resume:
    """根据 ID 获取指定求职者。"""
    resume = repository.get_by_id(resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="未找到对应的求职者简历",
        )

    return resume
