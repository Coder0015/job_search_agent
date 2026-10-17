from app.schemas.job import Job
from app.repositories.job_repository import JobRepository


class JobService:
    """负责招聘岗位相关的业务逻辑。"""

    def __init__(self, repository: JobRepository):
        self.repository = repository

    def search_jobs(
            self,
            *,
            keyword: str | None = None,
            city: str | None = None,
            category: str | None = None,
            min_salary: int | None = None,
            max_salary: int | None = None,
    ) -> list[Job]:
        """校验搜索条件，并查询符合要求的岗位。"""

        if (
                min_salary is not None
                and max_salary is not None
                and min_salary > max_salary
        ):
            raise ValueError("最低薪资不能高于最高薪资")

        return self.repository.search(
            keyword=keyword,
            city=city,
            category=category,
            min_salary=min_salary,
            max_salary=max_salary,
        )

    def get_job(self, job_id: str) -> Job | None:
        """根据岗位 ID 获取岗位。"""
        return self.repository.get_by_id(job_id)
