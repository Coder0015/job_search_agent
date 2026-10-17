from app.repositories.job_repository import JobRepository

repository = JobRepository()

jobs = repository.list_all()

print("岗位总数：", len(jobs))
print("第一条岗位：", jobs[0].title)

results = repository.search(
    city="北海",
    category="运营",
    min_salary=5000,
)

print("符合条件的运营岗位：", len(results))

for job in results[:3]:
    print(job)
    # print(job.title, job.salary_min, job.salary_max)
