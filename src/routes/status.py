from fastapi import APIRouter, HTTPException, Query
from typing import List
from pydantic import BaseModel
from src.models.service import Service
from src.models.status import Status
from src.utils.checker import check_service_status
from src.config import settings
from datetime import datetime
import asyncio

router = APIRouter(prefix="/status", tags=["Status"])

class StatusResponse(BaseModel):
    id: str
    service_id: str
    status: str
    latency_ms: float
    response_code: int | None
    error_message: str | None
    timestamp: str

class CheckAllResponse(BaseModel):
    message: str
    checked_services: int
    results: List[StatusResponse]

@router.post("/check-all", response_model=CheckAllResponse)
async def check_all_services():
    """
    Fetch all services, check their status, and store results in database
    """
    services = await Service.find_all().to_list()
    
    if not services:
        raise HTTPException(status_code=404, detail="No services found")
    
    results = []
    
    for service in services:
        status_data = await check_service_status(service.url, settings.REQUEST_TIMEOUT)

        status_record = Status(
            service_id=str(service.id),
            status=status_data["status"],
            latency_ms=status_data["latency_ms"],
            response_code=status_data["response_code"],
            error_message=status_data["error_message"]
        )

        await status_record.insert()
        
        results.append(StatusResponse(
            id=str(status_record.id),
            service_id=str(service.id),
            status=status_record.status,
            latency_ms=status_record.latency_ms,
            response_code=status_record.response_code,
            error_message=status_record.error_message,
            timestamp=status_record.timestamp.isoformat()
        ))
    
    return CheckAllResponse(
        message=f"Successfully checked {len(services)} services",
        checked_services=len(services),
        results=results
    )

@router.get("", response_model=List[StatusResponse])
async def get_status_logs(
    limit: int = Query(default=50, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    service_id: str | None = Query(default=None, description="Filter by service ID")
):
    """
    Get status logs with pagination and optional filtering by service_id
    """
    if service_id:
        query = Status.find(Status.service_id == service_id)
    else:
        query = Status.find_all()

    statuses = await query.sort(-Status.timestamp).skip(offset).limit(limit).to_list()
    
    return [
        StatusResponse(
            id=str(status.id),
            service_id=status.service_id,
            status=status.status,
            latency_ms=status.latency_ms,
            response_code=status.response_code,
            error_message=status.error_message,
            timestamp=status.timestamp.isoformat()
        )
        for status in statuses
    ]

@router.get("/latest", response_model=List[StatusResponse])
async def get_latest_status():
    """
    Get the latest status for each service
    """
    services = await Service.find_all().to_list()
    results = []
    
    for service in services:
        latest_status = await Status.find(
            Status.service_id == str(service.id)
        ).sort(-Status.timestamp).limit(1).first_or_none()
        
        if latest_status:
            results.append(StatusResponse(
                id=str(latest_status.id),
                service_id=latest_status.service_id,
                status=latest_status.status,
                latency_ms=latest_status.latency_ms,
                response_code=latest_status.response_code,
                error_message=latest_status.error_message,
                timestamp=latest_status.timestamp.isoformat()
            ))
    
    return results

@router.get("/count")
async def get_status_count(service_id: str | None = Query(default=None)):
    """
    Get total count of status records, optionally filtered by service_id
    """
    if service_id:
        count = await Status.find(Status.service_id == service_id).count()
    else:
        count = await Status.find_all().count()
    
    return {"count": count}
