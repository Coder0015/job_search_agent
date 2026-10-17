from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    resume_id: str = Field(min_length=1)


class CreateSessionResponse(BaseModel):
    session_id: str
    resume_id: str


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    session_id: str
    resume_id: str
    reply: str
    jobs: list[dict] = Field(default_factory=list)
