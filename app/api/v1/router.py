from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.places import router as places_router
from app.api.v1.trip_reels import router as trip_reels_router
from app.api.v1.trips import router as trips_router
from app.api.v1.video_media import router as video_media_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(places_router, prefix="/places", tags=["places"])
api_router.include_router(trips_router, prefix="/trips", tags=["trips"])
api_router.include_router(video_media_router, tags=["video-media"])
api_router.include_router(trip_reels_router, tags=["trip-reels"])
