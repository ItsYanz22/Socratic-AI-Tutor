from fastapi import APIRouter
from app.models.schemas import TutorRequest, TutorResponse

# Create a "router" for this feature
router = APIRouter(
    prefix="/tutor",  # All routes here will start with /tutor
    tags=["Socratic Tutor"]  # This creates a nice tag in the /docs
)


@router.post("/ask", response_model=TutorResponse)
async def ask_tutor(request: TutorRequest):
    # This is the "Socratic Wrapper" MVP.
    # It's not smart yet, but it proves the API works.

    # TODO: Add real call to ai_service.py in the next step

    socratic_response = f"This is a Socratic response to: '{request.prompt}'"

    return TutorResponse(response=socratic_response)