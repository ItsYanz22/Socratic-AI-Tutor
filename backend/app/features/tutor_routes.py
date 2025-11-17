from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel  # We need this for the new models

# Import all our Pydantic models from the schemas file
from app.models.schemas import TutorRequest, TutorResponse, SnippetRequest, SnippetResponse

from app.auth.dependencies import get_current_user
from app.services.ai_service import get_socratic_response
from app.services.supabase_service import log_snippet_request  # <-- This import is correct

router = APIRouter(
    prefix="/tutor",
    tags=["Socratic Tutor"]
)


@router.post("/ask", response_model=TutorResponse)
async def ask_tutor(request: TutorRequest, user=Depends(get_current_user)):
    # --- UPGRADED ---
    # Now we pass the prompt AND the chat history to the AI service
    ai_response = await get_socratic_response(
        prompt=request.prompt,
        chat_history=request.chat_history
    )

    return TutorResponse(response=ai_response)


# --- NEW SNIPPET ENDPOINT ---
@router.post("/get-snippet", response_model=SnippetResponse)
async def get_snippet(request: SnippetRequest, user=Depends(get_current_user)):
    # --- 1. LOG THE ACTION ---
    # We log that the user asked for a snippet.
    # We must create this function in supabase_service.py
    try:
        await log_snippet_request(user_id=user.id, challenge_id=request.challenge_id)
    except Exception as e:
        # Don't fail the request if logging fails, just print an error
        print(f"CRITICAL: Failed to log snippet request: {e}")

    # --- 2. RETURN THE HARD-CODED SNIPPET ---
    # This is our "answer key" for the hackathon MVP
    snippet_database = {
        "meity_pcap_1": "from scapy.all import rdpcap\n\n# Read the pcap file\npackets = rdpcap('your_file.pcap')",
        "isro_fits_1": "from astropy.io import fits\n\n# Open the FITS file\nhdu_list = fits.open('your_file.fits')"
    }

    snippet = snippet_database.get(request.challenge_id, "No snippet available for this challenge.")

    return SnippetResponse(snippet=snippet)