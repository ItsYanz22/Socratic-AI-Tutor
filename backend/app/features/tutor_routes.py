from fastapi import APIRouter, Depends
from app.models.schemas import TutorRequest, TutorResponse, SnippetRequest, SnippetResponse
from app.auth.dependencies import get_current_user
from app.services.ai_service import get_socratic_response
from app.services.supabase_service import log_snippet_request

router = APIRouter(
    prefix="/tutor",
    tags=["Socratic Tutor"]
)


@router.post("/ask", response_model=TutorResponse)
async def ask_tutor(request: TutorRequest, user=Depends(get_current_user)):
    # CALL THE AI SERVICE
    # This connects to the "smart" brain we built
    ai_response = await get_socratic_response(
        prompt=request.prompt,
        chat_history=request.chat_history
    )

    return TutorResponse(response=ai_response)


@router.post("/get-snippet", response_model=SnippetResponse)
async def get_snippet(request: SnippetRequest, user=Depends(get_current_user)):
    # Log the request
    try:
        await log_snippet_request(user_id=user.id, challenge_id=request.challenge_id)
    except Exception as e:
        print(f"CRITICAL: Failed to log snippet request: {e}")

    # Return the hard-coded snippet
    snippet_database = {
        "meity_pcap_1": "from scapy.all import rdpcap\n\n# Read the pcap file\npackets = rdpcap('your_file.pcap')",
        "isro_fits_1": "from astropy.io import fits\n\n# Open the FITS file\nhdu_list = fits.open('your_file.fits')"
    }

    snippet = snippet_database.get(request.challenge_id, "No snippet available for this challenge.")

    return SnippetResponse(snippet=snippet)