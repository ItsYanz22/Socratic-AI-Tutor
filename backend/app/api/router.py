from fastapi import APIRouter
# <-- Import peer_assist_routes
from app.features import tutor_routes, sandbox_routes, peer_assist_routes

api_router = APIRouter()

# Include the Socratic Tutor routes
api_router.include_router(tutor_routes.router)
# Include the Sandbox routes
api_router.include_router(sandbox_routes.router)
# Include the Peer Assist routes
api_router.include_router(peer_assist_routes.router) # <-- Add this line