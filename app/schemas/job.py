from pydantic import BaseModel, Field


class Job(BaseModel):
    """招聘岗位"""

    id: str = Field(description="岗位唯一标识")
    title: str = Field(description="岗位名称")
    company: str = Field(description="招聘公司名称")
    city: str = Field(description="工作城市")
    category: str = Field(description="岗位类别")

    salary_min: int = Field(
        ge=0,
        description="最低月薪，单位为人民币元",
    )
    salary_max: int = Field(
        ge=0,
        description="最高月薪，单位为人民币元",
    )

    description: str = Field(description="岗位描述")

    requirements: list[str] = Field(
        default_factory=list,
        description="岗位任职要求",
    )

    benefits: list[str] = Field(
        default_factory=list,
        description="岗位福利",
    )

    experience_requirement: str = Field(
        default="不限",
        description="工作经验要求",
    )

    education_requirement: str = Field(
        default="不限",
        description="学历要求",
    )

    is_demo: bool = Field(
        default=True,
        description="是否为演示岗位数据",
    )
