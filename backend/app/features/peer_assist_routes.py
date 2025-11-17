from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any

from app.auth.dependencies import get_current_user
from app.services.supabase_service import (
    create_peer_assist_request,
    get_open_assist_requests,
    claim_assist_request
)

router = APIRouter(
    prefix="/assist",
    tags=["Peer Assist"]
)


class AssistRequest(BaseModel):
    challenge_id: str


class AssistResponse(BaseModel):
    success: bool
    message: str
    assist_id: str | None = None


class QueueResponse(BaseModel):
    success: bool
    queue: List[Dict[str, Any]] = []


@router.post("/request", response_model=AssistResponse)
async def request_peer_assist(request: AssistRequest, user=Depends(get_current_user)):
    """
    A user who is stuck requests help from a peer.
    """
    assist_id = await create_peer_assist_request(
        user_id=user.id,
        challenge_id=request.challenge_id
    )

    if not assist_id:
        raise HTTPException(status_code=500, detail="Could not create assist request.")

    return AssistResponse(
        success=True,
        message="Help request submitted. A peer mentor will be notified.",
        assist_id=assist_id
    )


@router.get("/queue", response_model=QueueResponse)
async def get_assist_queue(user=Depends(get_current_user)):
    """
    A mentor checks the queue for open help requests.
    (In a real app, this would filter out requests they can't answer)
    """
    open_requests = await get_open_assist_requests()
    return QueueResponse(success=True, queue=open_requests)


@router.post("/claim/{assist_id}", response_model=AssistResponse)
async def claim_peer_assist(assist_id: str, user=Depends(get_current_user)):
    """
    A mentor claims an open help request.
    """
    # We pass the mentor's user.id to log who claimed it
    success = await claim_assist_request(assist_id=assist_id, mentor_id=user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Could not claim request. It may already be taken.")

    return AssistResponse(success=True, message="Request claimed successfully.")