import json

from app.agents.tools.search_jobs import create_search_job
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService


def main():
    # 这里手动创建 Service，仅用于独立测试
    repository = JobRepository()
    service = JobService(repository)

    tools = create_search_job(service)
    search_jobs_tool = tools[0]

    result = search_jobs_tool.invoke(
        {
            "city": "北海",
            "category": "运营",
            "min_salary": 5000,
            "limit": 3,
        }
    )

    data = json.loads(result)

    print("返回岗位数量：", data["count"])

    for job in data["jobs"]:
        print(
            job["title"],
            job["company"],
            job["salary_min"],
            job["salary_max"],
        )


if __name__ == "__main__":
    main()
