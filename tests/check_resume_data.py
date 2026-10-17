import json
from pathlib import Path

from app.schemas.resume import Resume

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESUME_DATA_PATH = PROJECT_ROOT / "app" / "data" / "resume.json"


def main():
    data_path = RESUME_DATA_PATH

    with data_path.open("r", encoding="utf-8") as file:
        raw_resumes = json.load(file)

    resumes = [Resume.model_validate(item) for item in raw_resumes]

    resume_ids = [resume.id for resume in resumes]

    assert len(resume_ids) == len(set(resume_ids)), "存在重复的简历 ID"

    print(f"成功加载 {len(resumes)} 份简历")

    for resume in resumes:
        print(
            f"ID: {resume.id} | "
            f"姓名: {resume.name} | "
            f"经验: {resume.years_of_experience} 年"
        )


if __name__ == "__main__":
    main()
