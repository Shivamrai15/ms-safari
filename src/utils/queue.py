from bullmq import Queue
from src.config import settings


queue = Queue("process-history", {
    "connection" : settings.REDIS_URL
})