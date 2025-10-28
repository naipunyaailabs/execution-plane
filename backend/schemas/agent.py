from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AgentBase(BaseModel):
    name: str
    agent_type: str
    llm_provider: str
    llm_model: str
    temperature: float
    system_prompt: Optional[str] = ""
    tools: List[str] = []
    max_iterations: int
    memory_type: str
    streaming_enabled: bool
    human_in_loop: bool
    recursion_limit: int

class AgentCreate(AgentBase):
    api_key: str  # This won't be stored, just used for initialization

class AgentInDB(AgentBase):
    agent_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AgentExecutionRequest(BaseModel):
    input: str
    thread_id: Optional[str] = None

class AgentExecutionResponse(BaseModel):
    response: str
    thread_id: str