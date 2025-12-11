from beanie import Document
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List

class AppInfo(BaseModel):
    app_version: str = Field(..., alias="appVersion")
    build_number: str = Field(..., alias="buildNumber")
    environment: Literal['development', 'staging', 'production']
    expo_version: str = Field(..., alias="expoVersion")
    release_channel: Optional[str] = Field(None, alias="releaseChannel")

    class Config:
        populate_by_name = True

class DeviceInfo(BaseModel):
    platform: Literal['ios', 'android', 'web']
    os_version: str = Field(..., alias="osVersion")
    device_model: Optional[str] = Field(None, alias="deviceModel")
    device_id: Optional[str] = Field(None, alias="deviceId")
    manufacturer: Optional[str] = None

    class Config:
        populate_by_name = True

class UserContext(BaseModel):
    user_id: Optional[str] = Field(None, alias="userId")
    is_authenticated: bool = Field(..., alias="isAuthenticated")

    class Config:
        populate_by_name = True

class NavigationContext(BaseModel):
    current_screen: str = Field(..., alias="currentScreen")
    previous_screen: Optional[str] = Field(None, alias="previousScreen")
    route_params: Optional[Dict[str, Any]] = Field(None, alias="routeParams")

    class Config:
        populate_by_name = True

class NetworkInfo(BaseModel):
    url: Optional[str] = None
    method: Optional[Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH']] = None
    status_code: Optional[int] = Field(None, alias="statusCode")
    response_time: Optional[float] = Field(None, alias="responseTime")
    request_headers: Optional[Dict[str, str]] = Field(None, alias="requestHeaders")
    response_body: Optional[str] = Field(None, alias="responseBody")

    class Config:
        populate_by_name = True

class ErrorLog(Document):
    message: str
    severity: Literal['low', 'medium', 'high', 'critical']
    error_code: Optional[str] = Field(None, alias="errorCode")
    timestamp: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = Field(None, alias="resolvedAt")
    
    app_info: AppInfo = Field(..., alias="appInfo")
    device_info: DeviceInfo = Field(..., alias="deviceInfo")
    user_context: Optional[UserContext] = Field(None, alias="userContext")
    navigation_context: Optional[NavigationContext] = Field(None, alias="navigationContext")
    network_info: Optional[NetworkInfo] = Field(None, alias="networkInfo")
    
    status: Literal['new', 'acknowledged', 'in_progress', 'resolved', 'ignored'] = 'new'
    assigned_to: Optional[str] = Field(None, alias="assignedTo")
    notes: Optional[List[str]] = None
    fingerprint: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Settings:
        name = "error_logs"

    class Config:
        populate_by_name = True
