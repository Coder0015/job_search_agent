import json

from langchain.tools import tool

from app.services.job_service import JobService


def create_search_job(job_service: JobService):
    @tool("search_jobs")
    def search_jobs(
            keyword: str | None = None,
            city: str | None = None,
            category: str | None = None,
            min_salary: int | None = None,
            max_salary: int | None = None,
            limit: int = 3,
    ) -> str:
        """搜索求职 AI 演示招聘岗位。

        当用户的求职意向已经足够明确，需要查找或推荐岗位时调用。

        如果用户的求职方向模糊，而且缺少影响推荐的关键信息，
        应当先向用户提问，不要直接进行宽泛搜索。

        Args:
            keyword: 岗位相关关键词，例如 Python、客户沟通。
            city: 工作城市或地区，例如北海。
            category: 岗位类别，例如运营、行政、技术开发。
            min_salary: 用户期望的最低月薪，单位为人民币元。
            max_salary: 用户能接受的最高月薪，单位为人民币元。
            limit: 最多返回多少个岗位，默认 3，最多 10 个。

        Returns:
            包含岗位实际信息的 JSON 字符串。
        """
        try:
            jobs = job_service.search_jobs(
                keyword=keyword,
                city=city,
                category=category,
                min_salary=min_salary,
                max_salary=max_salary,
            )
        except ValueError as exc:
            return json.dumps(
                {"error": str(exc)},
                ensure_ascii=False,
            )

        # 控制返回数量，避免一次向模型传入过多岗位信息
        limit = max(1, min(limit, 10))
        selected_jobs = jobs[:limit]

        if not selected_jobs:
            return json.dumps(
                {
                    "count": 0,
                    "jobs": [],
                    "message": (
                        "当前演示数据中没有找到符合条件的岗位。"
                        "不要编造岗位，可以向用户说明情况，"
                        "并询问是否愿意调整非必要条件。"
                    ),
                },
                ensure_ascii=False,
            )

        # 只返回推荐所需的字段，而不是整个 Job 对象
        results = [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "city": job.city,
                "category": job.category,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "description": job.description,
                "requirements": job.requirements,
                "benefits": job.benefits,
                "experience_requirement": job.experience_requirement,
                "education_requirement": job.education_requirement,
                "is_demo": job.is_demo,
            }
            for job in selected_jobs
        ]

        return json.dumps(
            {
                "count": len(results),
                "jobs": results,
                "is_demo_data": True,
            },
            ensure_ascii=False,
        )

    return [search_jobs]
