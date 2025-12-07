from beanie import Document
from datetime import datetime
from pydantic import Field

class Service(Document):
    name: str
    url: str
    metadata: dict | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "services"