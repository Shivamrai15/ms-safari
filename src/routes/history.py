from fastapi import APIRouter, Depends
from typing import List
from src.models.history import History
from src.utils.token import auth_middleware
from src.utils.queue import queue

router = APIRouter(prefix="/api/v1", tags=["History"])

@router.post("/history")
async def create_history(
    history_list: List[History],
    user: dict = Depends(auth_middleware)
):
    """Receive history data and push the entire list to the Redis queue via Celery."""
    
    data = [item.model_dump() for item in history_list]
    await queue.add("history_batch", data=data)

    return {
        "status": "queued",
        "message": f"{len(data)} history record(s) pushed as a single batch to the queue",
        "userId": user["userId"]
    }
