from fastapi import APIRouter
from app.features import tutor_routes

api_router = APIRouter()

# Include the Socratic Tutor routes
# All routes from tutor_routes.py will now be under /api/v1
api_router.include_router(tutor_routes.router)