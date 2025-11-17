from fastapi import APIRouter
from app.features import tutor_routes, sandbox_routes # <-- Import sandbox_routes

api_router = APIRouter()

# Include the Socratic Tutor routes
api_router.include_router(tutor_routes.router)
# Include the Sandbox routes
api_router.include_router(sandbox_routes.router) # <-- Add this line