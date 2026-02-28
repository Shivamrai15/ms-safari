from pydantic import BaseModel

class History(BaseModel):
    userId: str
    trackId: str
    songDuration: int
    playedDuration: int
    playedAt: str
