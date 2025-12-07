from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from src.models.service import Service
from beanie import PydanticObjectId

router = APIRouter(prefix="/services", tags=["Services"])

class ServiceCreate(BaseModel):
    name: str
    url: str
    metadata: dict | None = None

class ServiceUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    metadata: dict | None = None

class ServiceResponse(BaseModel):
    id: str
    name: str
    url: str
    metadata: dict | None = None
    created_at: str
    updated_at: str

@router.get("", response_model=List[ServiceResponse])
async def get_all_services():
    """Get all services"""
    services = await Service.find_all().to_list()
    return [
        ServiceResponse(
            id=str(service.id),
            name=service.name,
            url=service.url,
            metadata=service.metadata,
            created_at=service.created_at.isoformat(),
            updated_at=service.updated_at.isoformat()
        )
        for service in services
    ]

@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: str):
    """Get a single service by ID"""
    try:
        service = await Service.get(PydanticObjectId(service_id))
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        return ServiceResponse(
            id=str(service.id),
            name=service.name,
            url=service.url,
            metadata=service.metadata,
            created_at=service.created_at.isoformat(),
            updated_at=service.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid service ID: {str(e)}")

@router.post("", response_model=ServiceResponse, status_code=201)
async def create_service(service_data: ServiceCreate):
    """Create a new service"""
    service = Service(
        name=service_data.name,
        url=service_data.url,
        metadata=service_data.metadata
    )
    await service.insert()
    
    return ServiceResponse(
        id=str(service.id),
        name=service.name,
        url=service.url,
        metadata=service.metadata,
        created_at=service.created_at.isoformat(),
        updated_at=service.updated_at.isoformat()
    )

@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(service_id: str, service_data: ServiceUpdate):
    """Update an existing service"""
    try:
        service = await Service.get(PydanticObjectId(service_id))
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        if service_data.name is not None:
            service.name = service_data.name
        if service_data.url is not None:
            service.url = service_data.url
        if service_data.metadata is not None:
            service.metadata = service_data.metadata
        
        from datetime import datetime
        service.updated_at = datetime.now()
        await service.save()
        
        return ServiceResponse(
            id=str(service.id),
            name=service.name,
            url=service.url,
            metadata=service.metadata,
            created_at=service.created_at.isoformat(),
            updated_at=service.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid service ID: {str(e)}")

@router.delete("/{service_id}", status_code=204)
async def delete_service(service_id: str):
    """Delete a service"""
    try:
        service = await Service.get(PydanticObjectId(service_id))
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        await service.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid service ID: {str(e)}")
