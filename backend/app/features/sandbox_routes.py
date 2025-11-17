from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.services.supabase_service import create_poc_entry
from pydantic import BaseModel

router = APIRouter(
    prefix="/sandbox",
    tags=["Sandbox"]
)


class SubmitRequest(BaseModel):
    code: str
    challenge_id: str
    assists_used: int = 0


class SubmitResponse(BaseModel):
    success: bool
    message: str
    proof_id: str | None = None


@router.post("/submit", response_model=SubmitResponse)
async def submit_sandbox(request: SubmitRequest, user=Depends(get_current_user)):
    # This is our MVP "hack" for checking the solution
    if "expected_solution" not in request.code:
        return SubmitResponse(success=False, message="Incorrect solution. Try again!")

    # Solution is correct! Create the proof.
    entry_uuid = await create_poc_entry(
        user_id=user.id,
        challenge_id=request.challenge_id,
        assists=request.assists_used
    )

    if not entry_uuid:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Could not create proof entry in database.")

    return SubmitResponse(
        success=True,
        message="Challenge passed! Proof of Competency created.",
        proof_id=entry_uuid
    )