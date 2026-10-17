import json
from pathlib import Path

from app.schemas.job import Job

PROJECT_ROOT = Path(__file__).resolve().parents[1]

JOB_DATA_PATH = PROJECT_ROOT / "data" / "jobs.json"


class JobRepository:
    """负责读取、查询和筛选招聘岗位。"""

    def __init__(self, data_path: Path | None = None):
        self.data_path = data_path or JOB_DATA_PATH

        # 启动初始化时读取一次
        self._jobs = self._load_data()

        # 建立岗位 ID 索引
        self._jobs_by_id = {
            job.id: job
            for job in self._jobs
        }

    def _load_data(self) -> list[Job]:
        """从 JSON 加载并校验全部岗位。"""
        with self.data_path.open("r", encoding="utf-8") as file:
            raw_jobs = json.load(file)

        if not isinstance(raw_jobs, list):
            raise ValueError("岗位数据格式错误：最外层必须是列表")

        jobs = [
            Job.model_validate(item)
            for item in raw_jobs
        ]

        job_ids = [job.id for job in jobs]

        if len(job_ids) != len(set(job_ids)):
            raise ValueError("岗位数据中存在重复的 ID")

        return jobs

    def list_all(self) -> list[Job]:
        """返回内存中的全部岗位。"""
        return list(self._jobs)

    def get_by_id(self, job_id: str) -> Job | None:
        """根据 ID 从内存索引中查询岗位。"""
        return self._jobs_by_id.get(job_id)

    def search(
            self,
            *,
            keyword: str | None = None,
            city: str | None = None,
            category: str | None = None,
            min_salary: int | None = None,
            max_salary: int | None = None,
    ) -> list[Job]:
        """根据关键词、城市、类别和薪资范围筛选岗位。"""

        if (
                min_salary is not None
                and max_salary is not None
                and min_salary > max_salary
        ):
            raise ValueError("最低薪资不能高于最高薪资")

        keyword = keyword.strip().casefold() if keyword else None
        city = city.strip().casefold() if city else None
        category = (
            category.strip().casefold()
            if category
            else None
        )

        results = []

        # 直接筛选缓存数据，不再读取 JSON
        for job in self._jobs:
            searchable_text = " ".join([
                job.title,
                job.company,
                job.category,
                job.description,
                *job.requirements,
            ]).casefold()

            if keyword and keyword not in searchable_text:
                continue

            if city and city not in job.city.casefold():
                continue

            if category and category not in job.category.casefold():
                continue

            if (
                    min_salary is not None
                    and job.salary_max < min_salary
            ):
                continue

            if (
                    max_salary is not None
                    and job.salary_min > max_salary
            ):
                continue

            results.append(job)

        return results
