from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from src.config import settings
from src.models.service import Service
from src.models.status import Status
from src.models.error_log import ErrorLog

async def init_db():
    client = AsyncIOMotorClient(settings.MONGODB_URL)

    database = client[settings.DB_NAME]

    await init_beanie(
        database=database,
        document_models=[
            Service,
            Status,
            ErrorLog
        ]
    )