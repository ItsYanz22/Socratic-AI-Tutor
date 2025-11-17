from supabase import create_client, Client
from app.core.config import settings
import uuid
from typing import List, Dict, Any  # <-- Add this for type hinting

# This is the ADMIN client, using the SERVICE_ROLE_KEY.
# It can bypass Row Level Security and write to the DB.
supabase_admin_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)


async def create_poc_entry(user_id: str, challenge_id: str, assists: int = 0) -> str | None:
    """
    Creates the final "Proof of Competency" entry when a user
    successfully completes a sandbox.
    """
    entry_uuid = str(uuid.uuid4())
    try:
        data, error = await supabase_admin_client.table("proofs").insert({
            "id": entry_uuid,
            "user_id": user_id,
            "challenge_id": challenge_id,
            "assists_used": assists  # This should be a count of snippets + peer assists
        }).execute()

        if error:
            print(f"Supabase error in create_poc_entry: {error}")
            return None

        return entry_uuid
    except Exception as e:
        print(f"Exception in create_poc_entry: {e}")
        return None


async def log_snippet_request(user_id: str, challenge_id: str):
    """
    Logs an "assist" event to the assist_logs table when a user
    requests an "Emergency Snippet".
    """
    entry_uuid = str(uuid.uuid4())
    try:
        # This assumes you have created the 'assist_logs' table in Supabase
        data, error = await supabase_admin_client.table("assist_logs").insert({
            "id": entry_uuid,
            "user_id": user_id,
            "challenge_id": challenge_id,
            "type": "snippet",
            "status": "closed"  # A snippet request is instantly "closed"
        }).execute()

        if error:
            print(f"Error logging snippet request: {error}")
        else:
            print(f"Logged snippet assist for user {user_id}")

    except Exception as e:
        print(f"Exception in log_snippet_request: {e}")


# --- PEER ASSIST FUNCTIONS ---

async def create_peer_assist_request(user_id: str, challenge_id: str) -> str | None:
    """
    Logs a new "peer_request" to the assist_logs table.
    This creates an "open" ticket in the queue.
    """
    entry_uuid = str(uuid.uuid4())
    try:
        data, error = await supabase_admin_client.table("assist_logs").insert({
            "id": entry_uuid,
            "user_id": user_id,  # The user who is STUCK
            "challenge_id": challenge_id,
            "type": "peer_request",
            "status": "open"  # This is a new 'open' ticket
        }).execute()

        if error:
            print(f"Error creating peer assist request: {error}")
            return None
        return entry_uuid
    except Exception as e:
        print(f"Exception in create_peer_assist_request: {e}")
        return None


async def get_open_assist_requests() -> List[Dict[str, Any]]:
    """
    Fetches all help requests that are still 'open' for mentors.
    """
    try:
        # Selects all requests that are open and of type 'peer_request'
        data, error = await supabase_admin_client.table("assist_logs").select(
            "id, challenge_id, created_at, user_id"  # We only show these fields
        ).eq(
            "status", "open"
        ).eq(
            "type", "peer_request"
        ).order(
            "created_at", desc=False  # Oldest first
        ).execute()

        if error:
            print(f"Error getting assist queue: {error}")
            return []

        return data[1]  # data[1] contains the list of results
    except Exception as e:
        print(f"Exception in get_open_assist_requests: {e}")
        return []


async def claim_assist_request(assist_id: str, mentor_id: str) -> bool:
    """
    A mentor claims a request, updating its status to 'claimed'
    and logging who claimed it in the 'metadata' column.
    """
    try:
        # Updates the row *only if* it is still "open"
        data, error = await supabase_admin_client.table("assist_logs").update({
            "status": "claimed",
            "metadata": {"claimed_by": mentor_id}  # Logs who the mentor was
        }).eq(
            "id", assist_id
        ).eq(
            "status", "open"  # Ensures we don't claim a request twice
        ).execute()

        if error:
            print(f"Error claiming request: {error}")
            return False

        # Check if any row was actually updated
        if len(data[1]) > 0:
            print(f"Mentor {mentor_id} claimed request {assist_id}")
            return True
        else:
            print(f"Request {assist_id} was already claimed or does not exist.")
            return False

    except Exception as e:
        print(f"Exception in claim_assist_request: {e}")
        return False