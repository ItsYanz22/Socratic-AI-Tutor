from fastapi import APIRouter, Depends
from app.models.schemas import TutorRequest, TutorResponse
from app.auth.dependencies import get_current_user
from app.services.ai_service import get_socratic_response  # <-- Import our new service

router = APIRouter(
    prefix="/tutor",
    tags=["Socratic Tutor"]
)


@router.post("/ask", response_model=TutorResponse)
async def ask_tutor(request: TutorRequest): #, user = Depends(get_current_user)):
    # Now we call the real AI
    ai_response = await get_socratic_response(request.prompt)

    return TutorResponse(response=ai_response)