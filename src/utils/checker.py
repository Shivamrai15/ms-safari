import httpx
import time
from typing import Dict, Any

async def check_service_status(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Check the status of a service by making an HTTP request.
    
    Args:
        url: The URL to check
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing status, latency, response_code, and error_message
    """
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "status": "up" if response.status_code < 500 else "down",
                "latency_ms": round(latency_ms, 2),
                "response_code": response.status_code,
                "error_message": None
            }
    except httpx.TimeoutException:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "status": "down",
            "latency_ms": round(latency_ms, 2),
            "response_code": None,
            "error_message": "Request timeout"
        }
    except httpx.ConnectError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "status": "down",
            "latency_ms": round(latency_ms, 2),
            "response_code": None,
            "error_message": f"Connection error: {str(e)}"
        }
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "status": "down",
            "latency_ms": round(latency_ms, 2),
            "response_code": None,
            "error_message": f"Error: {str(e)}"
        }
