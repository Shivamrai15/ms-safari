from beanie import Document
from datetime import datetime
from pydantic import Field

class Status(Document):
    status: str
    service_id: str
    latency_ms: float
    response_code: int | None = None
    error_message: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "statuses"