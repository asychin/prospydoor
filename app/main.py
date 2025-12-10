"""
Prosody Participant Count Hook (PPCH)
Microservice to check for participants in Jitsi Meet rooms without joining the room itself.
"""
from fastapi import FastAPI, Depends, HTTPException, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
from typing import Optional
import logging

from .config import settings
from .middleware import verify_api_key

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="REST API to check for participants in Jitsi Meet rooms",
    docs_url="/docs",
    redoc_url="/redoc"
)


class RoomParticipantsResponse(BaseModel):
    """Response model with room participant information"""
    room_name: str
    exists: bool
    participant_count: int
    has_participants: bool
    participants: list[str] = []
    room_jid: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    version: str
    prosody_status: str


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    No authentication required
    """
    # Check Prosody availability
    prosody_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.prosody_url}/room_participants_api/health")
            if response.status_code == 200:
                prosody_status = "ok"
            else:
                prosody_status = f"error (status: {response.status_code})"
    except Exception as e:
        prosody_status = f"error ({str(e)})"
        logger.error(f"Prosody check error: {e}")
    
    return HealthResponse(
        status="ok",
        service=settings.app_title,
        version=settings.app_version,
        prosody_status=prosody_status
    )


@app.get(
    "/api/rooms/{room_name}/participants",
    response_model=RoomParticipantsResponse,
    dependencies=[Depends(verify_api_key)],
    summary="Get room participant information",
    description="Returns the number of participants in the specified room without needing to join it"
)
async def get_room_participants(
    room_name: str = Path(..., description="Room name (without domain)", example="LaterProvisionsPullAdorably")
):
    """
    Get room participant information via Prosody API
    
    Args:
        room_name: Jitsi room name
        
    Returns:
        Room information and participant count
        
    Raises:
        HTTPException: If request to Prosody fails
    """
    logger.info(f"Requesting info for room: {room_name}")
    
    try:
        # Request to Prosody HTTP API
        prosody_endpoint = f"{settings.prosody_url}/room_participants_api/room-participants/{room_name}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(prosody_endpoint)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Room {room_name}: {data.get('participant_count', 0)} participants")
                return RoomParticipantsResponse(**data)
            elif response.status_code == 400:
                logger.warning(f"Invalid request for room {room_name}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid room name"
                )
            else:
                logger.error(f"Prosody API error: status {response.status_code}")
                raise HTTPException(
                    status_code=502,
                    detail=f"Prosody communication error (status: {response.status_code})"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Connection error with Prosody: {e}")
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to Prosody server"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": settings.app_title,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "api_endpoint": "/api/rooms/{room_name}/participants",
        "authentication": "X-API-Key header required"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
