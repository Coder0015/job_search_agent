import json
from pathlib import Path

from app.schemas.resume import Resume

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESUME_DATA_PATH = (
        PROJECT_ROOT / "data" / "resume.json"
)


class ResumeRepository:
    """负责读取和查询示例求职者简历。"""

    def __init__(self, data_path: Path | None = None):
        self.data_path = data_path or RESUME_DATA_PATH

        # 初始化时读取一次数据
        self._resumes = self._load_data()

        # 建立索引，后续根据 ID 查询不需要遍历全部数据
        self._resumes_by_id = {
            resume.id: resume
            for resume in self._resumes
        }

    def _load_data(self) -> list[Resume]:
        """从 JSON 加载并校验全部简历。"""
        with self.data_path.open("r", encoding="utf-8") as file:
            raw_resumes = json.load(file)

        if not isinstance(raw_resumes, list):
            raise ValueError("简历数据格式错误：最外层必须是列表")

        resumes = [
            Resume.model_validate(item)
            for item in raw_resumes
        ]

        resume_ids = [resume.id for resume in resumes]

        if len(resume_ids) != len(set(resume_ids)):
            raise ValueError("简历数据中存在重复的 ID")

        return resumes

    def list_all(self) -> list[Resume]:
        """返回内存中的全部简历。"""
        return list(self._resumes)

    def get_by_id(self, resume_id: str) -> Resume | None:
        """根据 ID 从内存索引中查询简历。"""
        return self._resumes_by_id.get(resume_id)


if __name__ == '__main__':
    rr = ResumeRepository()
    print(rr.get_by_id(resume_id="resume_sales_001"))
