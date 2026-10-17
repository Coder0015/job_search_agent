from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_job_service
from app.schemas.job import Job
from app.services.job_service import JobService


job_router = APIRouter()


@job_router.get("/", response_model=list[Job])
def search_jobs(
    keyword: str | None = None,
    city: str | None = None,
    category: str | None = None,
    min_salary: int | None = Query(default=None, ge=0),
    max_salary: int | None = Query(default=None, ge=0),
    service: JobService = Depends(get_job_service),
) -> list[Job]:
    """根据条件搜索岗位。"""

    try:
        return service.search_jobs(
            keyword=keyword,
            city=city,
            category=category,
            min_salary=min_salary,
            max_salary=max_salary,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@job_router.get("/{job_id}", response_model=Job)
def get_job(
    job_id: str,
    service: JobService = Depends(get_job_service),
) -> Job:
    """获取岗位详情。"""

    job = service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="未找到对应的招聘岗位",
        )

    return job