from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from src.models.error_log import ErrorLog, AppInfo, DeviceInfo, UserContext, NavigationContext, NetworkInfo
from beanie import PydanticObjectId
from datetime import datetime
from typing import Literal, Dict, Any

router = APIRouter(prefix="/error-logs", tags=["Error Logs"])

class ErrorLogCreate(BaseModel):
    message: str
    severity: Literal['low', 'medium', 'high', 'critical']
    error_code: Optional[str] = Field(None, alias="errorCode")
    timestamp: Optional[datetime] = None
    
    app_info: AppInfo = Field(..., alias="appInfo")
    device_info: DeviceInfo = Field(..., alias="deviceInfo")
    user_context: Optional[UserContext] = Field(None, alias="userContext")
    navigation_context: Optional[NavigationContext] = Field(None, alias="navigationContext")
    network_info: Optional[NetworkInfo] = Field(None, alias="networkInfo")
    
    fingerprint: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True

class ErrorLogUpdate(BaseModel):
    status: Optional[Literal['new', 'acknowledged', 'in_progress', 'resolved', 'ignored']] = None
    assigned_to: Optional[str] = Field(None, alias="assignedTo")
    notes: Optional[List[str]] = None
    resolved_at: Optional[datetime] = Field(None, alias="resolvedAt")

    class Config:
        populate_by_name = True

class ErrorLogResponse(BaseModel):
    id: str
    message: str
    severity: Literal['low', 'medium', 'high', 'critical']
    error_code: Optional[str] = Field(None, alias="errorCode")
    timestamp: str
    resolved_at: Optional[str] = Field(None, alias="resolvedAt")
    
    app_info: AppInfo = Field(..., alias="appInfo")
    device_info: DeviceInfo = Field(..., alias="deviceInfo")
    user_context: Optional[UserContext] = Field(None, alias="userContext")
    navigation_context: Optional[NavigationContext] = Field(None, alias="navigationContext")
    network_info: Optional[NetworkInfo] = Field(None, alias="networkInfo")
    
    status: Literal['new', 'acknowledged', 'in_progress', 'resolved', 'ignored']
    assigned_to: Optional[str] = Field(None, alias="assignedTo")
    notes: Optional[List[str]] = None
    fingerprint: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True

class ErrorLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    data: List[ErrorLogResponse]

    class Config:
        populate_by_name = True

def error_log_to_response(error_log: ErrorLog) -> ErrorLogResponse:
    return ErrorLogResponse(
        id=str(error_log.id),
        message=error_log.message,
        severity=error_log.severity,
        error_code=error_log.error_code,
        timestamp=error_log.timestamp.isoformat(),
        resolved_at=error_log.resolved_at.isoformat() if error_log.resolved_at else None,
        app_info=error_log.app_info,
        device_info=error_log.device_info,
        user_context=error_log.user_context,
        navigation_context=error_log.navigation_context,
        network_info=error_log.network_info,
        status=error_log.status,
        assigned_to=error_log.assigned_to,
        notes=error_log.notes,
        fingerprint=error_log.fingerprint,
        metadata=error_log.metadata
    )

@router.post("", response_model=ErrorLogResponse, status_code=201)
async def create_error_log(error_data: ErrorLogCreate):
    """Create a new error log"""
    error_log = ErrorLog(
        message=error_data.message,
        severity=error_data.severity,
        error_code=error_data.error_code,
        timestamp=error_data.timestamp or datetime.now(),
        app_info=error_data.app_info,
        device_info=error_data.device_info,
        user_context=error_data.user_context,
        navigation_context=error_data.navigation_context,
        network_info=error_data.network_info,
        fingerprint=error_data.fingerprint,
        metadata=error_data.metadata
    )
    await error_log.insert()
    
    return error_log_to_response(error_log)

@router.get("/{error_log_id}", response_model=ErrorLogResponse)
async def get_error_log(error_log_id: str):
    """Get a single error log by ID"""
    try:
        error_log = await ErrorLog.get(PydanticObjectId(error_log_id))
        if not error_log:
            raise HTTPException(status_code=404, detail="Error log not found")
        
        return error_log_to_response(error_log)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid error log ID: {str(e)}")

@router.get("", response_model=ErrorLogListResponse)
async def get_error_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page", alias="pageSize"),
    severity: Optional[Literal['low', 'medium', 'high', 'critical']] = None,
    status: Optional[Literal['new', 'acknowledged', 'in_progress', 'resolved', 'ignored']] = None,
    platform: Optional[Literal['ios', 'android', 'web']] = None,
    environment: Optional[Literal['development', 'staging', 'production']] = None,
    assigned_to: Optional[str] = Query(None, alias="assignedTo")
):
    """Get all error logs with pagination and filtering"""
    query_filters = {}
    
    if severity:
        query_filters['severity'] = severity
    if status:
        query_filters['status'] = status
    if platform:
        query_filters['device_info.platform'] = platform
    if environment:
        query_filters['app_info.environment'] = environment
    if assigned_to:
        query_filters['assigned_to'] = assigned_to
    
    if query_filters:
        total = await ErrorLog.find(query_filters).count()
    else:
        total = await ErrorLog.find_all().count()
    
    skip = (page - 1) * page_size
    
    if query_filters:
        error_logs = await ErrorLog.find(query_filters).skip(skip).limit(page_size).to_list()
    else:
        error_logs = await ErrorLog.find_all().skip(skip).limit(page_size).to_list()
    
    return ErrorLogListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=[error_log_to_response(log) for log in error_logs]
    )

@router.patch("/{error_log_id}", response_model=ErrorLogResponse)
async def update_error_log(error_log_id: str, update_data: ErrorLogUpdate):
    """Update an error log (status, assignedTo, notes, resolvedAt)"""
    try:
        error_log = await ErrorLog.get(PydanticObjectId(error_log_id))
        if not error_log:
            raise HTTPException(status_code=404, detail="Error log not found")

        if update_data.status is not None:
            error_log.status = update_data.status
        if update_data.assigned_to is not None:
            error_log.assigned_to = update_data.assigned_to
        if update_data.notes is not None:
            error_log.notes = update_data.notes
        if update_data.resolved_at is not None:
            error_log.resolved_at = update_data.resolved_at
        
        await error_log.save()
        
        return error_log_to_response(error_log)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid error log ID: {str(e)}")
