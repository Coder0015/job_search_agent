from app.schemas.resume import Resume


def format_resume_context(resume: Resume) -> str:
    """将 Resume 转换为注入 Agent 系统提示词的稳定文本。"""
    lines = [
        f"求职者姓名：{resume.name}",
        f"最高学历：{resume.education}",
        f"工作年限：{resume.years_of_experience} 年",
        f"技能：{_join_or_default(resume.skills)}",
    ]

    if resume.career_summary.strip():
        lines.append(f"经历概述：{resume.career_summary.strip()}")
    else:
        lines.append("经历概述：未提供")

    lines.append("工作经历：")
    if not resume.work_experience:
        lines.append("- 未提供")
    else:
        for experience in resume.work_experience:
            lines.append(
                f"- 公司：{experience.company}；"
                f"职位：{experience.position}；"
                f"时间：{experience.duration}"
            )
            if experience.responsibilities:
                for responsibility in experience.responsibilities:
                    lines.append(f"  - 工作内容：{responsibility}")

    return "\n".join(lines)


def _join_or_default(values: list[str]) -> str:
    """将列表字段格式化，避免空列表产生误导性的空文本。"""
    cleaned = [value.strip() for value in values if value.strip()]
    return "、".join(cleaned) if cleaned else "未提供"
