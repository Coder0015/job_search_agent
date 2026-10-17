from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    """工作经历"""

    company: str = Field(description="公司名称")
    position: str = Field(description="担任的职位")
    duration: str = Field(description="工作时间")
    responsibilities: list[str] = Field(
        default_factory=list,
        description="主要工作内容",
    )


class Resume(BaseModel):
    """求职者简历"""

    id: str = Field(description="简历唯一标识")
    name: str = Field(description="求职者姓名")
    education: str = Field(description="最高学历")
    years_of_experience: int = Field(
        ge=0,
        description="工作年限",
    )
    skills: list[str] = Field(
        default_factory=list,
        description="技能列表",
    )
    work_experience: list[WorkExperience] = Field(
        default_factory=list,
        description="工作经历列表",
    )
    career_summary: str = Field(
        default="",
        description="个人经历概述",
    )
