from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class CommandRequest(BaseModel):
    command: str = Field(..., min_length=1, max_length=1000)

    @validator("command")
    def block_dangerous(cls, v):
        v = v.strip()
        dangerous = [
            r"rm\s+-rf\s+/",
            r":\(\)\{.*\};:",
            r"mkfs",
            r"dd\s+if=/dev/zero",
            r">\s*/dev/sd",
        ]
        for pattern in dangerous:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Command contains dangerous operations")
        return v


class CommandResponse(BaseModel):
    output: str
    exit_code: int
    executed_at: datetime
    cwd: str = "/workspace"


class ShellStatus(BaseModel):
    session_id: Optional[str]
    status: str
    created_at: Optional[datetime]
